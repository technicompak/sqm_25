
import werkzeug

import logging

from odoo import fields, http, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
_logger = logging.getLogger(__name__)
from odoo.osv import expression


class Controller(http.Controller):

    def main(self):
        pass