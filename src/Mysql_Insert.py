# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4 import QtCore, QtGui
from Ui_Mysql_Insert import Ui_MainWindow


# to insert into MysqlDatabase
import time
import pymysql
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer,Numeric,BigInteger,DateTime,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Table, MetaData
from sqlalchemy.sql.sqltypes import Integer
from xlrd import open_workbook
#to make GUI thread flexible
import threading
class MyThread(threading.Thread):
    '''
    the class for the thread running control
    '''
    def __init__(self,func,args,name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        
    def getResult(self):
         return self.args   

    def run(self):
        print 'starting',self.name,'at:',time.ctime()
        self.res = apply(self.func,self.args)
        print self.name,'finished at:',time.ctime()




class MainWindow(QMainWindow, Ui_MainWindow,threading.Thread):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.finish_target = 0
        self.total_target = 0
        self.flush_thread = 0
        
        self.filename = u''
#         self.user = 'root' 
#         self.password = '123456'
#         self.ip = '119.28.25.120'
#         self.db_name = 'test'
        self.user = '' 
        self.password = ''
        self.ip = ''
        self.db_name = ''
     
    def run(self):
        '''
        the thread function recording the voice
        '''
        print 'starting',self.name,'at:',time.ctime()
        self.res = apply(self.my_record)
        print self.name,'finished at:',time.ctime()    
  
        
    @pyqtSignature("")
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.filename = QtGui.QFileDialog.getOpenFileName(self,u'打开文件','/')
        self.lineEdit.setText(self.filename)
#         print unicode(self.filename)
    
    @pyqtSignature("")
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        insert_t = MyThread(self.read_file_and_execute_insertion,(self.filename,),self.read_file_and_execute_insertion.__name__)
        self.flush_thread = 1
        flush_t = MyThread(self.flush_target_label,(),self.flush_target_label.__name__)
        insert_t.setDaemon(True)
        flush_t.setDaemon(True)
        insert_t.start()
        flush_t.start()
        
    @pyqtSignature("QString")
    def on_lineEdit_2_textChanged(self, p0):
        """
        to set the database name
        """
        self.db_name = str(p0)

    @pyqtSignature("QString")
    def on_lineEdit_3_textChanged(self, p0):
        """
        to set the username
        """
        self.user = str(p0)
        
    @pyqtSignature("QString")
    def on_lineEdit_4_textChanged(self, p0):
        """
        to set the password
        """
        self.password = str(p0)
        
    @pyqtSignature("QString")
    def on_lineEdit_5_textChanged(self, p0):
        """
        to set the password
        """
        self.ip = str(p0)
    
    #dynamic to define a table Stock table class __tablename__
    def get_model(self,suffix):
        DynamicBase = declarative_base(class_registry=dict())
        
        class StockModel(DynamicBase):
            __tablename__ = '{suffix}'.format(suffix=suffix)
    
            id = Column(Integer,primary_key=True)
            PB = Column(Numeric(8,4)) 
            PE = Column(Numeric(8,4))   
            PE1 = Column(Numeric(8,4))   
            accumAdjFactor = Column(Integer)  
            actPreClosePrice  = Column(Numeric(8,4))   
            chgPct = Column(Numeric(8,4))   
            closePrice  = Column(Numeric(8,4))  
            dealAmount  = Column(BigInteger)  
            highestPrice  = Column(Numeric(8,4))  
            isOpen    = Column(Integer)
            lowestPrice = Column(Numeric(8,4))    
            marketValue = Column(BigInteger)   
            negMarketValue = Column(BigInteger)   
            openPrice  = Column(Numeric(8,4))    
            preClosePrice  = Column(Numeric(8,4))    
            turnoverRate = Column(Numeric(8,4))     
            turnoverValue  = Column(BigInteger)  
            turnoverVol = Column(BigInteger)   
            vwap = Column(Numeric(8,4))
            date = Column(DateTime)
    
        return StockModel()
           
        
        
    #create a type table
    def create_single_table(self,table_name,engine):
        meta_data = MetaData(engine)
        stock = Table(
                     table_name,
                     meta_data,
                     Column('id',Integer,primary_key = True),
                     Column('PB', Numeric(8,4)),
                     Column('PE', Numeric(8,4)),
                     Column('PE1', Numeric(8,4)),
                     Column('accumAdjFactor', Integer),
                     Column('actPreClosePrice', Numeric(8,4)),
                     Column('chgPct', Numeric(8,4)),
                     Column('closePrice', Numeric(8,4)),
                     Column('dealAmount', BigInteger),
                     Column('highestPrice', Numeric(8,4)),
                     Column('isOpen', Integer),
                     Column('lowestPrice',Numeric(8,4)),
                     Column('marketValue',BigInteger),
                     Column('negMarketValue',BigInteger),
                     Column('openPrice',Numeric(8,4)),
                     Column('preClosePrice',Numeric(8,4)),
                     Column('turnoverRate',Numeric(8,4)),
                     Column('turnoverValue',BigInteger),
                     Column('turnoverVol',BigInteger),
                     Column('vwap',Numeric(8,4)),
                     Column('date',DateTime),
                     )   
        meta_data.create_all(engine)   
    #execute single table insertion
    def table_insertion(self,**kwargs):
        index_name_list = kwargs.get('index_name_list')
        stock_list = kwargs.get('stock_list')
        
        user = self.user 
        password = self.password
        ip = self.ip
        db_name = self.db_name 
        
        target_location = 'mysql+pymysql://'+user+':'+password+'@'+ip+':3306/'+db_name
#         engine = sqlalchemy.create_engine('mysql+pymysql://root:123456@119.28.25.120:3306/test') 
#         print target_location
        engine = sqlalchemy.create_engine(target_location) 
       
        self.create_single_table(stock_list['secID'], engine)    
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        new_stock = self.get_model(str(stock_list['secID']))
        for attr in index_name_list:               
            if hasattr(new_stock,str(attr)):
                setattr(new_stock,str(attr),stock_list.get(attr))
            setattr(new_stock,'date',stock_list.get('date'))
        
        session.add(new_stock)
        session.commit()
        session.close()
        self.textBrowser.append(unicode('finish stock'+stock_list['secID']))
                   
    
    
    #read the excel file and return a map with the stockCode key to stockStruct value       
    def read_file_and_execute_insertion(self,file_name):
        file_name = str(file_name)
        wb = open_workbook(file_name)
    #     sheets_list = wb.sheet_names() 
        result = {}
        stock_list = {}
        index_name_list = []
        index_value_list = []
        # to init the last date field 
        date_time = ''
        for sheet in wb.sheets():
            if sheet.nrows:
                self.total_target = sheet.nrows
                self.label_5.setText(u'插入条目数:'+str(self.total_target))
                date_time = str(sheet.name).replace('dailydata-', '')
                for row in range(sheet.nrows):
                    if row == 0:
                        for col in range(sheet.ncols):
                           item = str(sheet.cell(row,col)).split('\'')[1]
                           index_name_list.append(item.replace('\'',''))
                    else:
                        for col in range(sheet.ncols):
                            if sheet.cell(row,col):
                                if col == 0:
                                    item = str(sheet.cell(row,col)).split('\'')[1]
                                else: 
                                    item = str(sheet.cell(row,col)).split(':')[1]
                                index_value_list.append(item)
                                stock_list[ index_name_list[col] ] = item
                        print stock_list
                        self.table_insertion(index_name_list=index_name_list,stock_list=stock_list)       
                        self.finish_target += 1
                       
            
    def flush_target_label(self):
        while self.flush_thread == 1:
             self.label_6.setText(u'完成条目数:'+str(self.finish_target))


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
