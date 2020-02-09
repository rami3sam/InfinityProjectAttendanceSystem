from __main__ import app,MAX_CAM_NO
from flask import request,render_template,redirect,flash
from core_functions import appDatabase,getSettings,setSettings

@app.route('/generalSettings',methods=['GET','POST'])
def generalSettings():
    cameraIPsList = []
    if request.method == 'GET':
        cameraIPsList = getSettings('cameraIPS',[])
        return render_template('generalSettings.html',MAX_CAM_NO=MAX_CAM_NO,cameraIPsList=cameraIPsList,len=len)
    elif request.method == 'POST':
        
        for i in range(100):
            cameraIPValue = request.form.get('cameraIP{}'.format(i))
            if cameraIPValue  not in [None,'']:
                cameraIPsList.append(cameraIPValue)
            else:
                break
        setSettings('cameraIPS',cameraIPsList)
    flash('Settings saved successfully','success')
    return redirect(request.url)
