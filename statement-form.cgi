#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##
## Форма создания/редактирования заявления
##

import dbconnect as dbc
import cgi
import auth
import os
import re

from datetime import datetime

import cgitb
cgitb.enable()

http_host = os.environ["HTTP_HOST"]

# Словарь переменных формы
data = {'lastname': '', 'firstname': '', 'secname': '', 'period_beg': '',
        'period_end': '', 'address': '', 'phone': '', 'course': '', 
        'groupname': '-', 'eduform': 'очная', 'edubasis': '', 'parent_lastname': '', 
        'parent_firstname': '', 'parent_secname': '', 'parent_phone': '', 
        'passport_type': 'паспорт', 'passport_number': '', 'passport_givenby': ''}

#
# Вывод формы заявления
#
def output_form(data, action, selected_id='', mode='enabled', bad_fields=[]):
    print "Content-type: text/html\n"

    print """
        <html><head><title>Форма заявления</title>
        <link rel="stylesheet" href="css/style.css" type="text/css" />
        <link type="text/css" rel="stylesheet" href="/JSCal2-1.9/src/css/jscal2.css" />
        <link type="text/css" rel="stylesheet" href="/JSCal2-1.9/src/css/border-radius.css" />
        <script src="/JQuery-1.11.2/jquery-1.11.2.min.js"></script>
        <script src="/JSCal2-1.9/src/js/jscal2.js"></script>
        <script src="/JSCal2-1.9/src/js/lang/ru.js"></script>
        
        <script type='text/javascript'>
            function back() {  history.go(-1)  }
    """
     
    if mode == 'readonly':
        print """
            $(document).ready(function() {
                $("#statement-form input[type!=button], #statement-form textarea")
                    .attr( {'readonly':true, 'style':'color: #757575'} );
                $("#statement-form select, #statement-form input[type=radio], #statement-form button").attr('disabled',true); 
           });
        """
        
        title = "Просмотр заявления (только для чтения)"

        buttons = """
            <input class='button longbtn' name='cancel' type='button' value='Закрыть' onclick="back()"/>
        """
    
    else:
        title = "Редактирование заявления"

        buttons = """
            <input class='button longbtn' name='save_data' type='submit' value='Сохранить и показать заявление' />
        """

    print """
            </script>        
        </head>
        <body>
    """

    if action == 'insert':
        print "<h1>Заявление на предоставление места в общежитии</h1>"
        
        if auth.ck_session():
            buttons += """
                <input class='button longbtn' name='cancel' type='button' value='Отмена' onclick="back()"/>
            """ 
    else:
        print "<h1>" + title + "</h1>"

    
    current_script_name =  os.path.basename(os.environ['SCRIPT_NAME'])

    print """
    <div class='content'>
    <form id='statement-form' method='post' action='""" + current_script_name + """' onkeypress='return event.keyCode != 13;'>
    <div class='section'>
    <h2>Данные об обучении</h2>"""

    print """
    <div class='field'>
    <span class='field_name'>Курс</span><br />
    <select name='course' size=1>"""

    for item in ['-', '1', '2', '3', '4', '5', '6']:
        selected = ''
        if data['course'] == item:
            selected = 'selected'
        print """<option value='"""+ item +"""' """+ selected +""">
                """+ item +"""</option>"""
    print """
    </select></div>"""


    print """
    <div class="field">
    <span class='field_name'>Группа</span><br />
    <input id='groupname' name='groupname' type='text' size='7' 
        value='"""+ data['groupname'] +"""' /><br />
    </div>"""


    print """
    <div class="field">
    <span class='field_name'>Форма обучения</span><br />
    """

    for item in ["очная", "заочная"]:
        checked = ''
        if data['eduform'] == item:
            checked = 'checked'
        print """<label><input id='eduform' name='eduform' type='radio' 
                value='"""+ item +"""' 
                """+ checked +""" />"""+ item +"""</label><br />"""


    year = datetime.now().year
    for field, val in zip(['period_beg', 'period_end'], ['01.09.' + str(year), '01.07.' + str(year+1)]):
        if data[field] == '':
            data[field] = val


    print """
    </div>

    <div class="field">
    <span class='field_name'>Основа обучения</span><br />
    <select name='edubasis' size=1>
    """
    
    for item in ["бюджетная", "внебюджетная", "целевая"]:
        selected = ''
        if data['edubasis'] == item:
            selected = 'selected'
        print """<option value='"""+ item +"""' """+ selected +""">
                """+ item +"""</option>"""

    print """
    </select>
    </div>
    </div>
    <div style="clear: both;"></div>


    <div class='section'>
    <h2>Персональные данные</h2>"""

    for label, name, code in zip(
            ['Фамилия', 'Имя', 'Отчество', 'Тип документа', 'Серия, номер'],
            ['lastname', 'firstname', 'secname', 'passport_type', 'passport_number'],
            ['', '', '<div style="clear: both;"></div>', '', '']):
        print """
        <div class="field">
        <span class='field_name'>"""+ label +"""</span><br />
        <input id='"""+name+"""' name='"""+name+"""' type='text' size='15'
            value='"""+ data[name] +"""' />
        </div>""" + code


    print """
    <div class="field">
    <span class='field_name'>Кем выдан, когда</span><br />
    <textarea id='passport_givenby' name='passport_givenby' 
    style='width: 355px; height: 35px;'>"""+ data['passport_givenby'] +"""</textarea>
    </div>
    <div style="clear: both;"></div>"""


    for label, name, size in zip(
            ['Адрес места регистрации (по паспорту)', 'Контактный телефон'],
            ['address', 'phone'],
            ['65', '40']):
        print """
        <div class="field">
        <span class='field_name'>"""+ label +"""</span><br />
        <input id='"""+ name +"""' name='"""+ name +"""' type='text'
            size='"""+ size +"""' value='"""+ data[name] +"""' />
        </div>"""

    print """</div><div style='clear: both;'></div>

    <div class='section'>
    <h2>Данные родителей</h2>"""


    for label, name, size in zip(['Фамилия', 'Имя', 'Отчество', 'Контактный телефон'],
                ['parent_lastname', 'parent_firstname', 'parent_secname', 'parent_phone'],
                ['15', '15', '15', '40']):

        print """
        <div class="field">
        <span class='field_name'>"""+ label +"""</span><br />
        <input id='"""+ name +"""' name='"""+ name +"""' type='text'
            size='"""+ size +"""' value='"""+ data[name] +"""' />
        </div>"""

    print """
    </div>
    <div style="clear: both;"></div>


    <div class='section'>
    <h2>Данные о заселении</h2>
    
    <div class="field">
    <span class='field_name'>Время проживания:</span><br />"""


    for text, field, trig, i in zip(['С ', ' по '],
                              ['period_beg', 'period_end'],
                              ['sel_bdate', 'sel_edate'],
                              ['1', '2']):
        print text +"""
        <input readonly id='"""+ field +"""' name='"""+ field +"""' 
                    type='text' size='8' maxlength='10' value='"""+ data[field] +"""' />
        <button class='button small-btn' id='"""+ trig +"""'>&#9660;</button>
        <script>
        RANGE_CAL_"""+ i +""" = new Calendar({
                             inputField: '"""+ field +"""',
                             dateFormat: '%d.%m.%Y',
                             trigger: '"""+ trig +"""',
                             bottomBar: false,
                             onSelect: function() {
                             this.hide();
                }});
        </script>
        """

    print """
    </div>
    </div>
    <div style="clear: both;"></div>

    <input name='template_name' type='hidden' value='statement-template' />
    
    """ + buttons + """    
    
 
    <input name='action' type='hidden' value='"""+ action +"""' />
    <input name='selected_id' type='hidden' value='"""+ selected_id +"""' />
</form>
</div>
</body></html>"""

    if bad_fields:
        print """<script>
        alert('Некоторые поля не заполнены или заполнены неверно.');"""

        for i in bad_fields:
            print "var "+ i +" = document.getElementById('"+ i +"');"
            print i +".setAttribute('style', 'border: 1px solid red');"

        print "</script>"

    return



#
# Запись/обновление данных
#
def save_data(form_data, action, selected_id = ""):

    if action == "insert":
        crit_list = []
        
        for key in ['lastname', 'firstname', 'secname', 'period_beg', 'period_end', 'passport_number']:
            if 'period' in key:
                crit_list.append(key + "=STR_TO_DATE('"+ form_data[key] +"', '%d.%m.%Y')")
            else:
                crit_list.append("LOWER(TRIM(" + key + ")) = LOWER(TRIM('"+ form_data[key] +"'))")

        qry_search_duplicate = """
          SELECT MAX(id) FROM statement
          WHERE """ + " AND ".join(crit_list)

        id_result = dbc.get_result_list(qry_search_duplicate)
        
        if id_result != [['None']]:
            action = "update"
            selected_id = id_result[0][0]
            
    if action == "insert":
        sql_query = "INSERT INTO statement ("
        for key in form_data.keys():
            sql_query += key +", "
        sql_query = sql_query.rstrip(', ')
        sql_query += ") VALUES ("


        for key in form_data.keys():
            if 'period' in key:
                sql_query += "STR_TO_DATE('"+ form_data[key] +"', '%d.%m.%Y'), "
            else:
                sql_query += "'"+ form_data[key] +"', "


        sql_query = sql_query.rstrip(', ')
        sql_query += ")"

    else:
        sql_query = "UPDATE statement SET "


        for key in form_data.keys():
            if 'period' in key:
                sql_query += key +"=STR_TO_DATE('"+ form_data[key] +"', '%d.%m.%Y'), "
            else:
                sql_query += key +"='"+ form_data[key] +"', "

        sql_query = sql_query.rstrip(', ')
        sql_query += " WHERE id='"""+ selected_id +"'"


    dbc.cursor.execute(sql_query)
    dbc.db.commit()
    dbc.cursor.close()

    print_statement(form_data)
    return



#
# Печать заявления
#
def print_statement(params):
    import urllib
    import urllib2

    params['template_name'] = 'statement-template'

    params = urllib.urlencode(params)

    # headers = {}
    req = urllib2.Request('https://'+ http_host +'/hostel/create_pdf.cgi', params, {})
    res = urllib2.urlopen(req)
    # print res.headers
    open_new_tab(res.read().rstrip('\n'))
    return



#
# Открытие заявления в новой вкладке
#
def open_new_tab(filename):
    print "Content-type: text/html\n"


    if not auth.ck_session():
        print """
        <html><head><title>Просмотр заявления</title>
        <link rel="stylesheet" href="css/style.css" type="text/css" />
        </head>
        <body>
        <div class='content'>
        <div class='section'>
        <p id='help_msg' style="font-weight: bold; color: #a10000;">Заявление сформировано и откроется в новом окне браузера.<br />
        Если этого не произошло - разрешите открытие всплывающих окон.</p>
        <a href=http://barnaul.fa.ru>Перейти на сайт филиала.</a>
        </div>
        </div>
        <script>
        link = "https://"""+ http_host +"""/hostel/statements/"""+ filename +"""";
        window.open(link,'_blank');
        setTimeout(function(){document.getElementById('help_msg').style.display = 'none'}, 10000);
        </script>
        </body>
        </html>
        """
        return
    else:
        print """
        <html><head><title>Просмотр заявления</title>
        <script>
        link = "https://"""+ http_host +"""/hostel/statements/"""+ filename +"""";
        window.open(link,'_blank');
        setTimeout(function(){document.location.href='statement.cgi'}, 5000);
        </script>
        </head>
        <body>
        <p>Вы будете перенаправлены на предыдущую страницу через 5 секунд.</p>
        </body>
        </html>
        """
    return


#
# Проверка полей ввода
#
def ck_form(form_data):
    data = form_data
    bad_fields = []
    
    for k in data:
        data[k] = re.sub(r'[\';:&%\^\$\*\\/#\{\}"<>]', '', data[k])
        if data[k] == '':
            bad_fields.append(k)

    return bad_fields



#
# Главная функция
#
def main():
    environ = dict(os.environ)
    # remove the query string from it
    del environ['QUERY_STRING']
    # parse the environment
    f = cgi.FieldStorage(environ=environ)
    # form contains no arguments from the query string!
    
    if "save_data" in f:
        form_data = {}
        for key in data:
            #if f.getfirst(""+ key +"", "") != '':
            form_data[key] = f.getfirst(key, '')

        bad_fields = ck_form(form_data)
        if bad_fields:
            output_form(form_data, '', '', '', bad_fields)
        else:
            save_data(form_data, f.getfirst("action"), f.getfirst("selected_id"))

    elif (("edit" in f or "print" in f or "view" in f) and
            "selected_id" in f and f["selected_id"].value is not None):
        selected_id = f.getfirst("selected_id")
        sql_query = "SELECT "
        for key in data:
            if 'period' in key:
                sql_query += "DATE_FORMAT("+ key +", '%d.%m.%Y') AS "+ key +", "
            else:
                sql_query += key +", "
        sql_query = sql_query.rstrip(', ')
        sql_query += " FROM statement WHERE id='"+ selected_id +"'"


        dbc.cursor_dict.execute(sql_query)

        row = dbc.cursor_dict.fetchone()
      
        dbc.cursor_dict.close()


        for key in data:
            data[key] = str(row[""+ key +""])

        if "print" in f:
            print_statement(data)
        elif "view" in f:
            output_form(data, 'update', selected_id, 'readonly')
        else:
            output_form(data, 'update', selected_id)
    else:
        output_form(data, 'insert')
    return



main()
