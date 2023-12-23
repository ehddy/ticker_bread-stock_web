
# modules
from ticker_bread.modules.Economy.Indicators import * 
from ticker_bread.modules.Stock.StockForLibrary import *
from ticker_bread.modules.Coporation.Disclosure import *



# from monitoring.views.auth_views import login_required
from  ticker_bread.modules.Visualize.dash_app import *
from ticker_bread.cache import cache
# from pybo.models import Question
from flask import Blueprint, url_for, render_template
from werkzeug.utils import redirect


# main_views가 인수로 전달, 첫 번째 인수 main은 블루프린트의 별칭
bp = Blueprint('main', __name__, url_prefix='/')



@bp.route('/')
def index():
    
    sq = Indicators()

    graph_fig = cache.get("graph_fig")
    if graph_fig is None:
        graph_fig = treemap()
        cache.set("graph_fig", graph_fig, timeout=300)
        
    graph_tree = graph_fig.to_json()

    recent_date = cache.get("recent_date")
    if recent_date is None:
        recent_date = sq.get_recent_date()
        cache.set("recent_date", recent_date, timeout=300)

    kospi_df = cache.get("kospi_df")
    if kospi_df is None:
        kospi_df = sq.get_recent_index_data('KS11')
        cache.set("kospi_df", kospi_df, timeout=300)
    
    kosdaq_df = cache.get("kosdaq_df")
    if kosdaq_df is None:
        kosdaq_df = sq.get_recent_index_data('KQ11')
        cache.set("kosdaq_df", kosdaq_df,timeout=300)


    kospi = [kospi_df['Close'][0], kospi_df['Change'][0], kospi_df['ChangeAmount'][0]]
    kosdaq = [kosdaq_df['Close'][0], kosdaq_df['Change'][0], kosdaq_df['ChangeAmount'][0]]
    # current_app.logger.info("info")
    # return redirect(url_for('question._list'))

    return render_template('main.html', kospi=kospi, kosdaq=kosdaq, recent_date=recent_date, graph_tree= graph_tree)
