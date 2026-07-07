#!/usr/bin/env python3
#
#  __init__.py
"""
Jinja2 templates.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# 3rd party
import jinja2
import nhle_map.templates
from domdf_python_tools.paths import PathPlus
from jinja2 import Environment
from nhle_map.utils import format_datetime, format_description

__all__ = ["render_template"]


templates = Environment(  # nosec: B701
		loader=jinja2.FileSystemLoader([str((PathPlus(__file__).parent).absolute()), str((PathPlus(nhle_map.templates.__file__).parent).absolute())]),
		undefined=jinja2.StrictUndefined,
		)

templates.globals["github_url"] = "https://github.com/domdfcoding/monuments-historique"
templates.globals["list"] = list
templates.globals["sorted"] = sorted
templates.globals["enumerate"] = enumerate
templates.globals["len"] = len
templates.globals["format_description"] = format_description
templates.globals["format_datetime"] = format_datetime

templates.filters["base64_encode"] = nhle_map.templates.base64_encode


def render_template(template: str, **kwargs) -> str:
	r"""
	Render the template with the given filename with the given parameters.

	:param template:
	:param \*\*kwargs:
	"""

	return templates.get_template(template).render(**kwargs)
