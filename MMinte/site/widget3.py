import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})


def getModels(id, modelFolder, url='https://p3.theseed.org/services/ProbModelSEED', runapp=True, wsurl='https://p3.theseed.org/services/Workspace'):
    '''
    This function allows metabolic models for individual species to be downloaded  to the user's local machine. From a genome ID, this function "communicates" with the ModelSEED platform, and sends a request for model reconstruction and gap filling with several default parameters. The model, in the Systems Biology Markup Language (SBML) format is then exported from the ModelSEED work space to a folder defined by the user in the user's local machine.


    :param id: genome ID of the model to be reconstructed and gapfilled using the ModelSEED platform.
    :param modelFolder: folder in the user's local machine where the model will be downloaded to.
    :param url:
    :param runapp:
    :param wsurl:
    :return: species model in model folder
    '''


    print id
    import json
    import requests
    import time
  
    cherrypy.log("We started the script to get models . We will reconstruct the model %s, get it from ModelSEED and export it to the folder: %s" %(id,modelFolder))


    token = 'un=mendessoares|tokenid=DF8D12F6-D45E-11E6-9B57-1B9C682E0674|expiry=1515277462|client_id=mendessoares|token_type=Bearer|SigningSubject=http://rast.nmpdr.org/goauth/keys/E087E220-F8B1-11E3-9175-BD9D42A49C03|this_is_globus=globus_style_token|sig=b6e67425ebe6c5aef7b52f5e3d38f4b5b615d401922379330709f88d827f7b53772ab3cb14d10d41821c9906238dafb17a93adcd006efd56d316fc4f9f9f38162d24b0bdff9a4f4311588ea8431bf77d0cbad6b6f4a07871fb7072106ff7ae15ca056f381c13486d2145d84466de0866a49591707d2b7d516de26738abed0b1f'
            
    # Create the headers for the request to the server.
    headers = dict()
    headers['AUTHORIZATION'] = token
    requests.packages.urllib3.disable_warnings()

    # See if the model is already available.
    input = dict()
    input['version'] = '1.1'
    input['method'] = 'Workspace.get'
    input['params'] = {'objects': ['/mendessoares/modelseed/'+id], 'metadata_only': 1}
    response = requests.post(wsurl, data=json.dumps(input), headers=headers, verify=False)

    if response.status_code != requests.codes.OK:
        # Create the body of the request for the ModelReconstruction() method.
        input['method'] = 'ProbModelSEED.ModelReconstruction'
        input['params'] = { 'genome': 'PATRIC:%s' %id, 'gapfill': 1, 'predict_essentiality': 0, 'media':'/chenry/public/modelsupport/media/ArgonneLBMedia' }

        # Send the request to the server and get back a response.
        # Added exception because the website gave an error and just stopped.


        response = requests.post(url, data=json.dumps(input), headers=headers, verify=False)

        if response.status_code != requests.codes.OK:
            response.raise_for_status()

        jobid = json.loads(response.text)['result'][0] # Get the output from the method in the response

        cherrypy.log('The job id for this particular run is: %s' %jobid)

        # Wait for the job to finish when model reconstruction is run as an app.
        if runapp:
            input['method'] = 'ProbModelSEED.CheckJobs'
            input['params'] = {}
            done = False
            while not done:
                response = requests.post(url, data=json.dumps(input), headers=headers, verify=False)
                if response.status_code != requests.codes.OK:
                    response.raise_for_status()
                output = json.loads(response.text)['result'][0]
                if jobid in output:
                    task = output[jobid]
                    print task['status']
                    cherrypy.log('The status of this job is %s' %task['status'])
                    if task['status'] == 'failed':
                        message = task['error'].split('\n')
                        for line in message: print line
                        raise Exception
                    elif task['status'] == 'completed':
                        done = True
                        cherrypy.log('The job has been completed')
                    else:
                        time.sleep(10)
                else:
                    raise Exception

                print task

    # Create the body of the request for the export_model() method.
    # When ModelSEED server is reliable we could switch back to this method.
    # input['method'] = 'ProbModelSEED.export_model'
    # input['params'] = { 'model': '/mendessoares/modelseed/'+id+'_model', 'format': 'sbml' }
    
    # Create the body of the request for the get() method.
    input['method'] = 'Workspace.get'
    input['params'] = { 'objects': [ '/mendessoares/modelseed/'+id+'/'+id+'.sbml' ] }
    
    # Send the request to the server and get back a response.            
    #added exception because the website gave an error and just stopped. I'll check in the morning how this looks. I'm not sure did it right (Lena)
    response = requests.post(wsurl, data=json.dumps(input), headers=headers, verify=False)
    if response.status_code != requests.codes.OK:
        response.raise_for_status()
        
    # The returned data is the URL of the shock node containing the sbml file.
    output = json.loads(response.text)['result'][0]
    cherrypy.log('The URL of the shock node containing the sbml file we want to export to our computer is %s' %output)

    # Get the sbml file from shock.
    response = requests.get(output[0][1]+'?download', headers={'AUTHORIZATION': 'OAuth '+token })
    if response.status_code != requests.codes.OK:
        response.raise_for_status()

    cherrypy.log('It seems the response status was OK.')

    # Store the SBML text in a file.    
    #with open('%s/%s.sbml' %(modelFolder,id)) as handle: # Use the genome ID as the file name
    #    cherrypy.log('You can find the model for %s in this path: %s.' %(id,('%s/%s.sbml' %(modelFolder,id))))
    #    handle.write(response.text) # File data is in the response object
            
    # Store the SBML text in a file.

    path2file = modelFolder+id+'.sbml'

    with open(path2file, 'w') as handle: # Use the genome ID as the file name
        handle.write(response.text) # File data is in the response object
