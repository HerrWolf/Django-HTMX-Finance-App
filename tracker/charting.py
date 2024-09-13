import plotly.express as px
import plotly.offline as pyo
from django.db.models import Sum

from tracker.models import Category


def render_plotly_figure(fig):
    config = {
        'displayModeBar': False,  # Desactiva la barra de modo
        'showTips': False,  # Desactiva las sugerencias
        'displaylogo': False  # Desactiva el logo de Plotly
    }
    return pyo.plot(fig, config=config, output_type='div', include_plotlyjs=False)


def plot_income_expenses_bar_chart(qs):
    x_vals = ['Income', 'Expenditure']

    total_income = qs.get_total_income()
    total_expenses = qs.get_total_expenses()

    fig = px.bar(
        x=x_vals,
        y=[total_income, total_expenses],
        labels={'x': 'Transaction Type', 'y': 'Amount'},
        title='Income vs Expenses',
        text=[total_income, total_expenses],
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        modebar_remove=[
            'zoom',
            'pan',
            'select',
            'lasso2d',
            'zoomIn2d',
            'zoomOut2d',
            'autoScale2d',
            'resetScale2d',
            'toImage'
        ]
    )

    return fig


def plot_category_pie_chart(qs):
    count_per_category = (
        qs.order_by('category').values('category')
        .annotate(total=Sum('amount'))
    )

    category_pks = count_per_category.values_list('category', flat=True).order_by('category')
    categories = Category.objects.filter(pk__in=category_pks).order_by('pk').values_list('name', flat=True)
    total_amounts = count_per_category.order_by('category').values_list('total', flat=True)

    fig = px.pie(values=total_amounts, names=categories)
    fig.update_layout(
        title_text='Total Amount per Category',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    return fig
