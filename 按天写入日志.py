import os
import logging.config
import json
class LogUtil:
    #创建一个字典，用户保存配置
    dictConf = {}
    # 配置文件的目录
    LOGGER_CONF_PATH = '../LOG_CFG'
    # 配置文件的名称
    LOGGER_CONF_NAME = 'logging.json'
    #构造方法
    def __init__(self):
        logJsonPath = self.LOGGER_CONF_PATH + os.sep + self.LOGGER_CONF_NAME
        self.dictConf = json.load(open(logJsonPath, 'r',encoding="utf-8"))
    #模块名
    LOGGER_NAME = 'runLogger'
    def getLogger(self,loggerName = LOGGER_NAME): #loggerName 运行日志的程序类
        logging.config.dictConfig(config=self.dictConf)
        logger = logging.getLogger(loggerName)
        return logger
        
if __name__ == '__main__':
    logUtil=LogUtil()
    log=logUtil.getLogger()
    log.info("这是一个信息日志")
    log.error("这是一个错误日志")