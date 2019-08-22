
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


    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'website': 'https://www.mufti.com'
}