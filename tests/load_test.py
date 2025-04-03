from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # tempo entre as requisições (em segundos)

    @task
    def load_another_endpoint(self):
        self.client.get("/user")  # outro endpoint
