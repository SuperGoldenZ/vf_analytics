import obsws_python as obs

class ObsHelper:

    def __init__(self):        
        self.cl = obs.ReqClient(host='localhost', port=4455, password=self.SECRET, timeout=3)


    def set_item_visible(self, sceneName="vf no text", itemName="P1Text"):                
        #result=self.client.call(requests.GetSceneItemId(sceneName=sceneName,sourceName=itemName))
        #item_id=result.getSceneItemId()
        #self.client.call(requests.SetSceneItemEnabled(sceneName=sceneName, sceneItemId=item_id, sceneItemEnabled=False))
        return None

    def start_recording(self):        
        self.cl.start_record()

    def stop_recording(self):        
        stop_result = self.cl.stop_record()
        return stop_result.output_path
