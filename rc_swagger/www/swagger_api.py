import inspect

import frappe
from frappe import _dict
from docstring_parser import parse
import docstring_parser
import jinja2
import os
import yaml
import json
import logging

no_cache = 1
base_template_path = "www/swagger_api.html"

from frappe.utils import get_site_name




def get_context(context=None):
	import_all_modules()
	logging.basicConfig(filename="openapi.log")
	# context.methods = get_whitelisted_methods()
	# context.resources = get_resources()
	jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.getcwd()+"/../apps/rc_swagger/rc_swagger/www/"))
	template = jinja_env.get_template("openapi.yaml")
	methods, tags = get_whitelisted_methods()
	yaml_out = template.render(methods=methods,tags=tags)

	python_dict = yaml.load(yaml_out,Loader=yaml.SafeLoader)

		
	output = json.dumps(python_dict, indent=2)
	context.data = output

	return context


def get_whitelisted_methods():
	logging.basicConfig(filename="openapi.log")

	result = []
	tags = []
	for method in frappe.whitelisted:
		if "frappe" in method.__module__ or "erpnext" in method.__module__:
			continue
		method_docstring = method.__doc__
		parsed_doc = parse(method_docstring)
		result.append({
			"name":method.__module__+"."+method.__name__,
			"parameters":{},
			"description":parsed_doc.long_description.replace("\n","<br>") if parsed_doc.long_description is not None else None,
			"summary":parsed_doc.short_description,
			"tags":["App "+method.__module__.split(".")[0]],
			"success":parsed_doc.returns.description if parsed_doc.returns is not None else "success"
		})
		for param in inspect.signature(method).parameters.values():
			result[-1]["parameters"][param.name] = {
				'type':'string'
			}
		for param in parsed_doc.params:
			result[-1]["parameters"][param.arg_name]={
				'type':param.type_name.replace('str','string'),
				'description':param.description,
			}
		if len(parsed_doc.meta) != 0:
			logging.error(parsed_doc.meta)
		for meta in parsed_doc.meta:
			if type(meta) != docstring_parser.DocstringMeta:
				continue
			if meta.args == ['tags']:
				for tag in meta.description.split(","):
					result[-1]["tags"].append(tag)
					if tag not in tags:
						tags.append(tag)
			elif meta.args == ['methods']:
				for method in meta.description.split(","):
					result[-1][method]="True"

	logging.error(tags)
	return result,tags
		

def pkg_submodules(package, recursive=True):
	import importlib
	import pkgutil
	""" Return a list of all submodules in a given package, recursively by default """

	if isinstance(package, str):
		try:
			package = importlib.import_module(package)
		except ImportError:
			return []

	submodules = []
	for _loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
		full_name = package.__name__ + "." + name

		try:
			submodules.append(importlib.import_module(full_name))
		except ImportError:
			continue
		except:
			continue

		if recursive and is_pkg:
			submodules += pkg_submodules(full_name)

	return submodules 

def import_all_modules():
	modules_list = frappe.db.get_list('API Modules',fields=["module_name","recursive"])
	for module in modules_list:
		pkg_submodules(module["module_name"],module["recursive"])