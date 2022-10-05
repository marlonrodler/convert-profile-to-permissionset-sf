import os
import subprocess
import json

profileName = input('Profile name: ')
permissionSetName = input('Permission Set name: ')

permissionSetPath = 'force-app/main/default/permissionsets/'+permissionSetName+'.permissionset-meta.xml'

def updatePermissionSet():
    print('============================== Update Permission Set ==============================')
    os.system('sfdx force:data:record:update -s PermissionSet -i '+newPermissionSetId+' -v "'+permissionSetFields+'"')

def getPermissionsFromProfile():
    profile = profileName

    if profile == 'Admin':
        profile = 'Administrador do sistema' #System Admin - For organizations that are in the English language
    queryProfile = 'sfdx force:data:soql:query -q "SELECT FIELDS(ALL) FROM Profile WHERE Name IN ({name}) LIMIT 1" --json'.format(name="'"+profile+"'")

    selectProfiles = subprocess.Popen(queryProfile, shell=True, stdout=subprocess.PIPE).stdout
    
    returnProfiles =  selectProfiles.read()
    global jsonProfiles 
    jsonProfiles = json.loads(returnProfiles)

    if jsonProfiles["status"] == 1:
        print('Profile not found!')
        exit()

def getPermissionFromPermissionsSet():
    queryPermission = 'sfdx force:data:soql:query -q "SELECT FIELDS(ALL) FROM PermissionSet WHERE Name IN ({name}) LIMIT 1" --json'.format(name="'"+permissionSetName+"'")

    selectPermissionsSet = subprocess.Popen(queryPermission, shell=True, stdout=subprocess.PIPE).stdout
    
    returnPermissionsSet =  selectPermissionsSet.read()
    jsonPermissionsSet = json.loads(returnPermissionsSet)

    global newPermissionSetId
    global newPermissionSet

    newPermissionSet = {}
    recordProfile = jsonProfiles["result"]["records"][0]
    recordPermissionSet = jsonPermissionsSet["result"]["records"][0]
    
    for key in recordPermissionSet.keys():
        if key == 'Id':
            newPermissionSetId = recordPermissionSet[key]

        if key.find('Permission') != -1:
            if key in recordProfile and recordProfile[key] == True and key != 'PermissionsManageExternalConnections':
                newPermissionSet[key] = recordProfile[key]

def preparePermissionSetFields():
    jsonNewPermissionSet = json.dumps(newPermissionSet)

    global permissionSetFields
    permissionSetFields = jsonNewPermissionSet.replace("{","").replace("}","").replace("'","").replace(",","").replace(": ","=").replace("\"","")

def createPermissionSet():
    sfdxConvert = 'sfdx shane:profile:convert -p "'+profileName+'" -n "'+permissionSetName+'"'
    os.system(sfdxConvert)
    os.system('sfdx force:source:deploy -p ' + permissionSetPath)
    
def retrievePackageXML():
    os.system('sfdx force:source:retrieve --manifest manifest/package.xml')

retrievePackageXML()
createPermissionSet()
getPermissionsFromProfile()
getPermissionFromPermissionsSet()
preparePermissionSetFields()
updatePermissionSet()
