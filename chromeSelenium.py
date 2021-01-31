from selenium import webdriver
from selenium.webdriver import Chrome
from importlib import import_module
import sys
#not using it for now...
#driver = Chrome(r"chromedriver.exe",)
driver=None
def dynamic_import(abs_module_path, class_name):
	module_object = import_module(abs_module_path)
	target_class = getattr(module_object, class_name)
	return target_class	
#this function allows dynamically import [library,class etc]
def importScript(package,driver):
	if package in sys.modules:
		del sys.modules[package]
	return dynamic_import(package,package)(driver)

modelName='glassdoorModel'
#saving time for recreate webrowser driver.
while True:
	model=importScript(modelName,driver)
	input('type for retry')
