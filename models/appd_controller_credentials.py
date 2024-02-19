class AppDControllerCredentials:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + token}
