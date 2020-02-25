from __main__ import app
from DatabaseClient import MAX_CAM_NO
from flask import request,render_template,redirect,flash
import DatabaseClient

@app.route('/generalSettings',methods=['GET','POST'])
def generalSettings():
    databaseClient = DatabaseClient.DatabaseClient()
    cameraIPsList = []
    if request.method == 'GET':
        cameraIPsList = databaseClient.getSettings('cameraIPS',[])
        return render_template('generalSettings.html',MAX_CAM_NO=MAX_CAM_NO,cameraIPsList=cameraIPsList,len=len)
    elif request.method == 'POST':
        
        for i in range(DatabaseClient.MAX_CAM_NO):
            cameraIPValue = request.form.get('cameraIP{}'.format(i))
            if cameraIPValue  not in [None,'']:
                cameraIPsList.append(cameraIPValue)
        databaseClient.setSettings('cameraIPS',cameraIPsList)
    flash('Settings were saved successfully','success')
    return redirect(request.url)
