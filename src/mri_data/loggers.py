# from loguru import logger


# class FileLogger:
#     def __init__(self):
#         self.logger = logger.bind(new_file="")

#     def log(self, level, message, new_file=""):
#         self.logger = logger.bind(new_file=new_file)
#         self.logger.log(level, message)


# class Formatter:
#     def __init__(self):
#         self.padding = 0
#         self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"

#     def format(self, record):
#         length = len("{name}:{function}:{line}".format(**record))
#         self.padding = max(self.padding, length)
#         record["extra"]["padding"] = " " * (self.padding - length)
#         return self.fmt
