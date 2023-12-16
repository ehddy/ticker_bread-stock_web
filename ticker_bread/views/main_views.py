from flask import Blueprint, url_for, render_template

# modules
from ticker_bread.modules.Economy.Indicators import * 
from ticker_bread.modules.Stock.StockForLibrary import *
from ticker_bread.modules.Coporation.Disclosure import *


# , current_app
from werkzeug.utils import redirect
# from monitoring.views.auth_views import login_required
from  ticker_bread.modules.Visualize.dash_app import *

# from pybo.models import Question


# main_views가 인수로 전달, 첫 번째 인수 main은 블루프린트의 별칭
bp = Blueprint('main', __name__, url_prefix='/')
@bp.route('/') 
def index():
    sq = Indicators()
    graph_fig = treemap()
    graph_tree = graph_fig.to_json()
    # 최근 장 종료 날짜 가져오기
    recent_date = sq.get_recent_date()
    kospi_df = sq.get_recent_index_data('KS11')
    kosdaq_df = sq.get_recent_index_data('KQ11')

    kospi = [kospi_df['Close'][0], kospi_df['Change'][0], kospi_df['ChangeAmount'][0]]
    kosdaq = [kosdaq_df['Close'][0], kosdaq_df['Change'][0], kosdaq_df['ChangeAmount'][0]]
    # current_app.logger.info("info")
    # return redirect(url_for('question._list'))

    return render_template('main.html', kospi=kospi, kosdaq=kosdaq, recent_date=recent_date, graph_tree= graph_tree)
