from flask import Blueprint,render_template,request,url_for,jsonify, flash,session,redirect

user=Blueprint("user",__name__,static_folder="static",template_folder="template")