from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings

from .forms import TransactionForm
from .models import Transaction
from .filters import TransactionFilter

from django_htmx.http import retarget

from .charting import render_plotly_figure, plot_income_expenses_bar_chart, plot_category_pie_chart
from .resources import TransactionResource


def index(request):
    return render(request, "tracker/index.html")


@login_required
def transactions_list(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)
    transaction_page = paginator.page(1)

    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()

    context = {
        'transactions': transaction_page,
        'filter': transaction_filter,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': total_income - total_expenses,
    }

    if request.htmx:
        return render(request, "tracker/partials/transactions_container.html", context)

    return render(request, "tracker/transactions_list.html", context)


@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            context = {
                'message': 'Transaction was add successfully!',
            }

            return render(request, "tracker/partials/transactions_success.html", context)
        else:
            context = {
                'form': form,
            }
            response = render(request, "tracker/partials/create_transaction_htmx.html", context)
            return retarget(response, '#transaction-block')

    context = {
        'form': TransactionForm(),
    }

    if not request.htmx:
        return render(request, "tracker/partials/create_transaction.html", context)

    return render(request, "tracker/partials/create_transaction_htmx.html", context)


@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction.save()

            context = {
                'message': 'Transaction was updated successfully!',
            }

            return render(request, "tracker/partials/transactions_success.html", context)
        else:
            context = {
                'form': form,
                'transaction': transaction,
            }

            response = render(request, "tracker/partials/update_transaction_htmx.html", context)
            return retarget(response, '#transaction-block')

    context = {
        'form': TransactionForm(instance=transaction),
        'transaction': transaction,
    }

    if request.htmx:
        return render(request, "tracker/partials/update_transaction_htmx.html", context)
    else:
        return redirect('transactions-list')


@login_required
@require_http_methods(['DELETE'])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()

    context = {
        'message': 'Transaction was deleted successfully!',
    }

    return render(request, "tracker/partials/transactions_success.html", context)


@login_required
def get_transactions(request):
    import time
    time.sleep(1)
    page = request.GET.get('page', 1)

    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)

    context = {
        'transactions': paginator.page(page),
    }

    return render(request, "tracker/partials/transactions_container.html#transaction_list", context)


@login_required
def transactions_charts(request):
    import time
    time.sleep(.3)
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    income_expense_bar = plot_income_expenses_bar_chart(transaction_filter.qs)
    category_income_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='income')
    )
    category_expense_pie = plot_category_pie_chart(
        transaction_filter.qs.filter(type='expense')
    )

    context = {
        'filter': transaction_filter,
        'income_expense_barchart': render_plotly_figure(income_expense_bar),
        'category_income_piechart': render_plotly_figure(category_income_pie),
        'category_expense_piechart': render_plotly_figure(category_expense_pie),
    }

    if request.htmx:
        return render(request, 'tracker/partials/charts_container.html', context)

    return render(request, "tracker/charts.html", context)


@login_required
def export(request):
    if request.htmx:
        return HttpResponse(headers={'HX-Redirect': request.get_full_path()})

    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related('category')
    )

    data = TransactionResource().export(transaction_filter.qs)
    # response = HttpResponse(data.csv, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    response = HttpResponse(data.json, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="transactions.json"'
    
    return response