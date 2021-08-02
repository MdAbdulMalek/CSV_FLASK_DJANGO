from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.http.response import JsonResponse
import json
import os
import pandas as pd
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
from django.utils import *
from django.templatetags.static import static
from Convert.settings import BASE_DIR, STATICFILES_DIRS, STATIC_ROOT
from django.core.files.base import File
from django.conf import settings as django_settings
import numpy as np
import re
import mimetypes


def strip_string(s):
    s = str(s)
    if "in" in s.split():
        s1 = s.replace("in", "").rstrip()
    elif "in." in s.split():
        s1 = s.replace("in.", "").rstrip()
    else:
        s1 = s
    tmp = re.split("-| ", s1)
    tmp = list(filter(lambda x: x != "", tmp))
    if len(tmp) == 1 and "/" in tmp[0]:
        tmp_1 = tmp[0].split("/")
        num, denom = tmp_1[0], tmp_1[1]
        return float(num) / float(denom)
    if len(tmp) == 1:
        return float(tmp[0])
    if len(tmp) > 1:
        tmp_1 = float(tmp[0])
        tmp_2 = tmp[1].split("/")
        num, denom = tmp_2[0], tmp_2[1]
        dec = float(num) / float(denom)
        return tmp_1 + dec

    return float(tmp[0])

def find_labels(cat_feat_ind_dict, cat_lab, findings):
    tmp_feat = []
    tmp_lab = []
    tmp_conf = []

    for f in findings:
        lab = f[0]
        conf = f[1]
        label_ind = cat_feat_ind_dict[lab]
        label = cat_lab[label_ind]
        tmp_lab.append(label)
        tmp_conf.append(conf)
        tmp_feat.append(lab)

    return tmp_lab, tmp_conf, tmp_feat
# Create your views here.

client_filename = ""
sanveo_filename = ""
output_filename = ""

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/files")

ppp = os.getcwd()

qqq = "\\static\\outputs\\"

rrr = ppp + qqq

OUTPUT_FOLDER = rrr.replace( "\\", "\\\\")

#OUTPUT_FOLDER = 'C:\\Users\\DCL\\Convert\\static\\outputs\\' ###os.path.join(BASE_DIR, "static/outputs")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def home(request):

    return render(request, "index.html")
    #return HttpResponse('Home Page')

def upload_client(request):
    global client_filename
	# check if the post request has the file part
    if 'source_fileName' not in request.FILES: ##change
        resp = JsonResponse({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.FILES.getlist('source_fileName')  ##change
	
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.name):  ###
            client_filename = "client.csv"
            path = os.path.join(django_settings.STATIC_ROOT, client_filename, 'w')  ###
            #path = os.path.join(UPLOAD_FOLDER, client_filename)
            if os.path.exists(path):
                os.remove(path)
            #file.save(path)
            success = True
            
        else:
            errors[file.name] = 'File type is not allowed' ###

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = JsonResponse(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = JsonResponse({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = JsonResponse(errors)
        resp.status_code = 400
        return resp

def upload_sanveo(request):
    
    global sanveo_filename


	# check if the post request has the file part
    if 'source_fileName_Sanveo' not in request.FILES:
        resp = JsonResponse({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
	
    files = request.FILES.getlist('source_fileName_Sanveo')
	
    errors = {}
    success = False
	
    for file in files:
        if file and allowed_file(file.name):
            sanveo_filename = "sanveo.csv"
            path = os.path.join(django_settings.STATIC_ROOT, sanveo_filename, 'w')
            #path = os.path.join(UPLOAD_FOLDER, sanveo_filename)
            if os.path.exists(path):
                os.remove(path)

            #file.save(path)
            success = True
            
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = JsonResponse(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = JsonResponse({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = JsonResponse(errors)
        resp.status_code = 400
        return resp



def processs(request):
    global client_filename
    global output_filename

    check_msg= ""

    resp = {}
    ## Processing client and sanveo file
    client_file = os.path.join(UPLOAD_FOLDER, client_filename)
    df_client = pd.read_csv(client_file)

    sanveo_file = os.path.join(UPLOAD_FOLDER, sanveo_filename)
    df_sanveo = pd.read_csv(sanveo_file)


    tmp_cols = request.POST.getlist('sourceHeaderFieldsClient')
    selected_cols = tmp_cols[0].split(',')


    list_check = False
    print(f"Sanveo Availabe Columns \n\n")
    print(df_sanveo.columns)

    print(f"Client Availabe Columns\n\n")
    print(df_client.columns)
    for s in selected_cols:
        if s not in df_sanveo.columns:
            print(f"{s} not found!")
            list_check = True
    if list_check:
        check_msg = "Some column names didn't match"
        resp['message_match'] = check_msg
        resp['flag'] = 0
        return resp

    else:
        check_msg = "All column names matched"

    
    df_client_work = df_client[selected_cols].copy(deep=True)

    
    df_sanveo_work = df_sanveo[selected_cols].copy(deep=True)


    if "Size" in selected_cols:
        df_client_work["Size"] = df_client["Size"].map(lambda x: strip_string(x)) ###
        df_sanveo_work["Size"] = df_sanveo_work["Size"].map(lambda x: strip_string(x))  ###

    df_client_work = df_client_work.applymap(lambda x: str(x).lower())
    df_sanveo_work = df_sanveo_work.applymap(lambda x: str(x).lower())
    client_feat = list(df_client_work.agg(" ".join, axis=1))
    cat_feat = list(df_sanveo_work.agg(" ".join, axis=1))
    cat_lab = list(df_sanveo["ID"].values)

    cat_feat_ind_dict = dict((key, val) for val, key in enumerate(cat_feat))

    feat_2_label_dict = {}
    label_2_feat_dict = {}

    for i, f in enumerate(cat_feat):
        feat_2_label_dict[f] = cat_lab[i]
        label_2_feat_dict[cat_lab[i]] = f

    result = []
    conf_list = []

    for ind, sample in enumerate(client_feat):
        sample_number = "sample_number_" + str(ind + 1)
        findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=1)
        pred_labels, pred_confs, features = find_labels(cat_feat_ind_dict, cat_lab, findings)
        label = pred_labels[0]
        conf = pred_confs[0]
        conf_list.append(conf)
        if conf == 100:
            result.append(label)
        elif conf > 85 and conf < 100:
            findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=3)
            pred_labels, _, _ = find_labels(cat_feat_ind_dict, cat_lab, findings)
            result.append(pred_labels)
        else:
            findings = process.extract(sample, cat_feat, scorer=fuzz.ratio, limit=5)
            pred_labels, _, _ = find_labels(cat_feat_ind_dict, cat_lab, findings)
            result.append(pred_labels)

    df_client_work["Predicted_label"] = result
    df_client_work["Confidence"] = conf_list

    output_filename = client_filename.split('.')[0] + "_" + "output.csv"
    if os.path.exists(os.path.join(OUTPUT_FOLDER, output_filename)):
        os.remove(os.path.join(OUTPUT_FOLDER, output_filename))


    df_client_work.to_csv(os.path.join(OUTPUT_FOLDER, output_filename))

    msg = "Processing Finished"
    down_msg = "Download the output file"

    resp['message_match'] = check_msg
    resp['message_finish'] = msg
    resp['flag'] = 1
    resp['download_msg'] = down_msg

    #return resp
    return HttpResponse(json.dumps(resp), content_type="application/json")

def download(request):
    global output_filename
    path = os.path.join(OUTPUT_FOLDER, output_filename, 'r')

    #return send_file(path, as_attachment=True)
        # resp = FileResponse(open(path, 'rb'))

    fl = open(path, 'r')

    mime_type, _ = mimetypes.guess_type(path)
    resp = HttpResponse(fl, content_type=mime_type)
    resp['Content-Disposition'] = "attachment; filename=%s" % output_filename

    return resp