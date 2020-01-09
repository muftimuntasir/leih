
{
    'name': 'LEIH',
    'version': '1.0.0',
    'category': 'hospital service',
    'description': """
This module is to configure modules related to an association.
==============================================================

It installs the profile for associations to manage events, registrations, memberships, 
membership products (schemes).
    """,
    'author': 'BLF Team',
    'depends': [],
    'data': [
        'diagnosis_room/diagnosis_room_view.xml',
        'Department/department_view.xml',
        'Doctors/doctors_view.xml',
        'Patients/patients_view.xml',
        'Diagnosis/diagonosis_view.xml',
        'Group/diagnosisgroup_view.xml',
        'examine_entry/examinationentry_view.xml',
        'bill_register/bill_register_view.xml',
        'sample/sticker_view.xml',
        'examine_entry/sample_type_view.xml',
        'sample/pending_in_lab_view.xml',
        'sample/report_view.xml',
        'bill_register/report/report_bill_register.xml',
        'bill_register/report/bill_report_menu.xml',
        'sample/report/report_sample_report.xml',
        'sample/report/sample_report_menu.xml',
        'sample/common_admin_view.xml',
        'bill_register/add_bill_view.xml',
        'package/examine_package_view.xml',
        'laundry/laundry_product_view.xml',
        'laundry/cleaning_view.xml',
        'blood/blood_donar.xml',
        'blood/blood_receiver.xml',
        'laundry/laundry_receive_view.xml',

        'diagnosis_room/report/report_diagnosis_room_layout.xml',
        'diagnosis_room/report/diagnosis_room_print_menu.xml',
        'Department/report/report_department_layout.xml',
        'Department/report/department_print_menu.xml',
        'Doctors/report/report_doctor_layout.xml',
        'Doctors/report/doctor_print_menu.xml',
        'Patients/report/report_patients_layout.xml',
        'Patients/report/patients_print_menu.xml',

        'expense/expense_view.xml',
        'expense/expense_pending_view.xml',
        'expense/expense_cancel_view.xml',


        'Group/report/report_group_layout.xml',
        'Group/report/group_print_menu.xml',
        'Diagnosis/report/report_diagnosis_layout.xml',
        'Diagnosis/report/diagnosis_print_menu.xml',

        'examine_entry/report/report_examine_entry_layout.xml',
        'examine_entry/report/examine_entry_print_menu.xml',


    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'website': 'https://www.mufti.com'
}