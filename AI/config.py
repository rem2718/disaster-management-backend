from dotenv import set_key, dotenv_values


class Config:
    def __init__(self, env_file):
        self.env_file = env_file
        self.env_vars = dotenv_values(env_file)

    def get(self, var):
        return self.env_vars.get(var)

    def update(self, values):
        for var, val in values.items():
            set_key(self.env_file, var, val)
        self.env_vars = dotenv_values(self.env_file)


config = Config(".env")
