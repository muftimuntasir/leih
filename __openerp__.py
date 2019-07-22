
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
        'Room/room_view.xml',
        'Department/department_view.xml',
        'Doctors/doctors_view.xml',
        'Patients/patients_view.xml',
        'Diagnosis/diagonosis_view.xml',
        'Group/group_view.xml',
        'Testentry/testentry_view.xml',
        'Investigation/investigation_view.xml'
        

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'website': 'https://www.mufti.com'
}