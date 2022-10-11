import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from lxml import etree
import re
import config

#Gets all table links in the current folder
def get_url_list(html_save_path):
    url_list=[]
    file  = os.listdir(html_save_path)
    for data_id in file:
        url=html_save_path+'/'+data_id
        if url.endswith ( ".html" ):
            table_url=[]
            table_url.append('html_table')
            table_url.append(data_id)
            table_url.append(url)
            url_list.append(table_url)
    return url_list

#Gets the row and column values of the table, entered as html text#
def getRowColumn(table):
    contentTree = etree.HTML(table, parser=etree.HTMLParser(encoding='utf-8'))
    contentTree=romove_hide_table(contentTree)
    row=0
    col=0
    links = contentTree.xpath('.//tr')
    if len(links) != 0:
        row=len(links)
        for i in range(len(links)):
            tds=links[i].xpath('.//td')
            ths=links[i].xpath('.//th')
            tempcol=len(tds)+len(ths)
            for j in range(len(tds)):
                colspan=tds[j].xpath('.//@colspan')
                if len(colspan)!= 0:
                    tempcol+=(int(colspan[0])-1)
                else:
                    continue
                
            for h in range(len(ths)):
                colspan=ths[h].xpath('.//@colspan')
                if len(colspan)!= 0 :
                    tempcol+=(int(colspan[0])-1)
                else:
                    continue
            if tempcol>=col:
                col=tempcol
    return row,col

#Adds the characteristic lengths of the cell to equal
def padding(table):
    max_len=0
    for i in table:
        features=i[1]
        for feature in features:
            for value in range(len(feature)):
                feature[value]=feature[value]+1
            if (len(feature) >= max_len):
                max_len=len(feature)
    for i in table:
        features=i[1]
        for feature in features:
            while(len(feature)<max_len):
                feature.append(0)
    return table

#Calculate the rows and rows of nested cells
def nest_cell(cell_init=[[-1,-1],[-2,-2]],cell_new=[[-3,-3],[-4,-4]]):
    result_init=[]
    if len(cell_init) == 1 :
        if cell_init[0][0] == -1 and cell_init[0][1] == -1:
            return cell_new
        else:
            for i in cell_init:
                for j in cell_new:
                    temp=[]
                    for g in i:
                        temp.append(g)
                    for h in j:
                        temp.append(h)
                    result_init.append(temp) 
    else:
        for i in cell_init:
            for j in cell_new:
                temp=[]
                for g in i:
                    temp.append(g)
                for h in j:
                    temp.append(h)
                result_init.append(temp)
    return result_init

#Split all the cells of the table#
def splitTable(row,col,table,table_encoder_init=[],encoder_init=[[-1,-1]],table_rank=0):
    contentTree = etree.HTML(table, parser=etree.HTMLParser(encoding='utf-8'))
    end = True
    nest_table_dict={}
    while(end):
        links = contentTree.xpath('//tr')
        table={}
        table_encoder=[]
        for u in range(col):
            table[u]=[]
        row=0
        for i in range(len(links)):
            tds=links[i].xpath('.//td')
            ths=links[i].xpath('.//th')
            td_ths=[]
            td_ths.extend(tds)
            td_ths.extend(ths)
            this_td=0
            column=0
            has_table=0
            for td_th in td_ths:
                nest_table=td_th.xpath('.//table')
                if len(nest_table)>0:
                    has_table=1
                    nest_table[0].getparent().remove(nest_table[0])
                    
                colspan=td_th.xpath('.//@colspan')
                rowspan=td_th.xpath('.//@rowspan')
                td_text_get=td_th.xpath('.//text()')
                td_text=''.join(td_text_get)
                td_encoder=[]
                if len(rowspan)!= 0 and len(colspan) == 0:
                    while len(table[column])>row:
                        column=column+1 
                    for n in range(int(rowspan[0])):
                        td_encoder.append([len(table[column]),column])
                        if  column in table.keys():
                            row_value=table[column]
                            row_value.append(td_text)
                        else :
                            table[column]=td_text
                    column=column+1
                elif len(rowspan)== 0 and len(colspan)!= 0:
                    while len(table[column])>row:
                        column=column+1 
                    for n in range(int(colspan[0])):
                        td_encoder.append([len(table[column]),column])
                        if column in table.keys():
                            row_value=table[column]
                            row_value.append(td_text)
                        else :
                            table[column]=td_text
                        column=column+1
                elif len(rowspan)!= 0 and len(colspan)!= 0:
                    while len(table[column])>row:
                        column=column+1 
                    for c in range(int(colspan[0])):
                        for r in range(int(rowspan[0])):
                            td_encoder.append([len(table[column]),column])
                            if column in table.keys():
                                row_value=table[column]
                                row_value.append(td_text)
                            else :
                                table[column]=td_text
                        column=column+1
                else:
#                     print (str(len(table[column])) +"  行"+ str(row)+" 列"+str(column))
                    while len(table[column])>row:
                        column=column+1 
                    td_encoder.append([len(table[column]),column])
                    if column in table.keys():
                        row_value=table[column]
                        row_value.append(td_text)
                    else :
                        table[column]=td_text
                    column=column+1
#                 print("td_encoder"+str(td_encoder))
                if(has_table==1):
#                     print("td_encoder 命中"+str(td_encoder)+"初始的为"+str(encoder_init))
                    nest_table_str=etree.tostring(nest_table[0],encoding="utf-8").decode()
                    nest_table_dict[nest_table_str]=nest_cell(encoder_init,td_encoder)
                    
                    break
                
                td_encoder=nest_cell(encoder_init,td_encoder)
                table_encoder.append([td_text,td_encoder,table_rank])
            if(has_table==1):
                table_encoder=[]
                break
            row=row+1
        if (row >= len(links) or (row==0 and col==0)):
            end=False
#     print(table_encoder)
    if (len(nest_table_dict)>0 ):
        rank_add=1
        for nest_tabel_1 in nest_table_dict.keys():
            row,col=getRowColumn(nest_tabel_1)
#             print("调用嵌套表格:"+str(nest_table_dict[nest_tabel_1]))
#             print("调用嵌套表格:"+str(row)+'  '+str(col))
            splitTable(row,col,nest_tabel_1,table_encoder_init,nest_table_dict[nest_tabel_1],table_rank=(table_rank+rank_add))
            rank_add=rank_add+1
    for each_init in table_encoder:
        table_encoder_init.append(each_init)
    return table_encoder_init,nest_table_dict

#Get the web table from the local URL#
def paquHtml(url):
    soup=BeautifulSoup(open(url,encoding='utf-8'),features='html.parser')  #features值可为lxml
    return soup

#Delete table hidden tables. When calculating the rows and rows of a table
def romove_hide_table(contentTree):
    del_td=contentTree.xpath('//td')
    for j in del_td:
        hide_table=j.xpath('.//table')
        for h in hide_table:
            h.getparent().remove(h)
        
    return contentTree

#Convert all web tables in the folder to a list#
def get_tables_list(data_url):
    url_list=get_url_list(data_url)
    table_list=[]
    for i in tqdm(url_list):
        record=[]
        name=i[0]+i[1]
        url=i[2]
        html=paquHtml(url)
        tables=html.find('table')
        num=0
        table_str=str(tables).replace(u'\xa0','')
        row,col= getRowColumn(table_str)
        try :
            tablesplit,borw=splitTable(row,col,table_str,table_encoder_init=[],encoder_init=[[-1,-1]])
        except Exception as e :
            print('There is an error in the web table format')
        tablesplit=padding(tablesplit)
        record.append(i[0])
        record.append(i[1])
        record.append(num)
        record.append(tablesplit)
        record.append(url)
        num=num+1
        table_list.append(record)
    return table_list
