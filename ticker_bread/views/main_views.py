from flask import Blueprint, url_for, render_template


# , current_app
from werkzeug.utils import redirect
# from monitoring.views.auth_views import login_required

# from pybo.models import Question

# main_views가 인수로 전달, 첫 번째 인수 main은 블루프린트의 별칭
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    
    

    # current_app.logger.info("info")
    # return redirect(url_for('question._list'))

    return render_template('main.html')
