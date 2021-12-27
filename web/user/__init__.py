from flask import Blueprint,render_template,request,url_for,jsonify, flash

user=Blueprint("user",__name__,static_folder="static",template_folder="template")