from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
import itertools

class ReportEmpShiftXlsx(models.AbstractModel):
    _name = 'report.de_emp_shift_management.employee_shift_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
    
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format(
            {'font_size': 11, 'align': 'vcenter', 'bg_color': '#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format114 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True,'border':True})
        format14 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True,'left':True ,'right':True,'top':True,'bottom':True})
        format5 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})
        format15 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False,'border':True})
       
        sheet = workbook.add_worksheet("Customer Export")
    
        sheet.merge_range(0,3, 0, 6,"Employee Shift Allocation",format4) 
    

        wiz_obj=self.env['wizard.report.emp.shift'].browse(data['ids'])
      
        
        
        # query="""select esa.id as id,
        #                 esa.employee_id as employee_id,
        #                 esa.date_from as date_from,
        #                 esa.date_to as date_to, 
        #                 sd.date_of_week as date_of_week,
        #                 sd.shift_id as shift_id,
        #                 shof.day_of_week as weekoffday,
        #                 shof.date_of_week as weekoffdate,
        #                 esa.shift_id as shift_id from employee_shift_alloc esa
        #                 left join
        #                 shift_days sd 
        #
        #
        #                  on esa.id = sd.shift_allocation_id
        #
        #                 left join
        #                 shift_offdays shof 
        #                 on esa.id = shof.shift_allocation_id
        #                 where date_from >= %(date_from)s and  date_to <= %(date_to)s
        #
        #
        #
        #      """    
        
        query="""select esa.id as id,
                        esa.employee_id as employee_id,
                        esa.date_from as date_from,
                        esa.date_to as date_to,
                         esa.shift_id as shift_id
                        from employee_shift_alloc esa
                        
                        where date_from >= %(date_from)s and  date_to <= %(date_to)s
        
        
     
             """         
        args = {
            
            'date_from': wiz_obj.date_from,
            'date_to':wiz_obj.date_to,
           
        }
        self.env.cr.execute(query, args)
        rs_moves = self._cr.dictfetchall()
        
        offdays_query="""select shiftoff.shift_allocation_id as id,
                        shiftoff.day_of_week as weekoffday,
                        shiftoff.date_of_week as weekoffdate from shift_offdays shiftoff
                        left join
                        employee_shift_alloc esa 
                        on esa.id = shiftoff.shift_allocation_id
                        where date_from >= %(date_from)s and  date_to <= %(date_to)s
                        order by weekoffdate asc
                          
        """
        
        self.env.cr.execute(offdays_query, args)
        weekends = self._cr.dictfetchall()
        
        ondays_query="""select sd.shift_allocation_id as id,
                                sd.date_of_week as date_of_week,
                                sd.shift_id as shift_id from shift_days sd
                                left join
                                employee_shift_alloc esa 
                                on esa.id = sd.shift_allocation_id
                                where date_from >= %(date_from)s and  date_to <= %(date_to)s"""
                                  
        
        self.env.cr.execute(ondays_query, args)
        workdays = self._cr.dictfetchall() 
        
   

            
        grouper = itertools.groupby(rs_moves, key=lambda x: x['employee_id'])
        val={}
        for key, group in grouper:
            valdict=[]
            for g in group:
                valdict.append(g)
            
          
            val[self.env['hr.employee'].browse([key]).name] = valdict
     

        row=4
        for emp in val:
            sheet.merge_range(row,0,row, 1,'Employee:',format4)
            sheet.merge_range(row,2,row, 3,emp,format4)
            sheet.write(row , 5,'From:', format4)
            sheet.write(row , 6,val[emp][0]['date_from'].strftime("%d-%b-%Y"), format5)
            row+=1
                
            sheet.write(row , 0,'Shift:', format4)
            shift_name= self.env['emp.shift'].browse([val[emp][0]['shift_id']]).name
            sheet.write(row , 1,shift_name, format5)
            sheet.write(row , 5,'to:', format4)
            sheet.write(row , 6,val[emp][0]['date_to'].strftime("%d-%b-%Y"), format5)
            
            row+=2
            sheet.merge_range(row,0,row, 5,'Weekends',format14)
            row+= 1
            sheet.merge_range(row,0,row, 2,'Date',format114)
            sheet.merge_range(row,3,row, 5,'Day',format114)
            
            row +=1
            for rec in val[emp]:
                for offday in weekends:
                    if rec['id'] == offday['id']:
                        
                        sheet.merge_range(row,0,row,2,offday['weekoffdate'].strftime("%d-%b-%Y"),format15)
                        day_name =self.env['emp.weekoff'].browse([offday['weekoffday']]).name
                        sheet.merge_range(row,3,row,5,day_name,format15)
                        row+=1
                        
                row+=2
                sheet.merge_range(row,0,row, 5,'Working days',format14)
                row+=1
                sheet.merge_range(row,0,row, 2,'Date',format114)
                sheet.merge_range(row,3,row, 5,'shift',format114)
                # 
                for onday in workdays:
                    if rec['id'] == onday['id']:
                        sheet.merge_range(row,0,row,2,onday['date_of_week'].strftime("%d-%b-%Y"),format15)
                        shift_name=self.env['emp.shift'].browse([onday['shift_id']]).name
                        sheet.merge_range(row,3,row,5,shift_name,format15)
                        row+=1
                
                         
            row+=2            
      
