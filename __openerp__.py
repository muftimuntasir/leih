
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
    'depends': ['sale'],
    'data': [
  
        'security/leih_security.xml',
        'security/ir.model.access.csv',
        'wizard/cc_collection_view.xml',
        'wizard/detail_component_view.xml',

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
        'sample/report_delivered_view.xml',
        'sample/report_view.xml',
        'bill_register/report/report_bill_register.xml',
        'bill_register/report/bill_report_menu.xml',
        'sample/report/report_sample_report.xml',
        'sample/report/sample_report_menu.xml',
        'sample/report/report_detail.xml',
        'sample/report/report_detail_menu.xml',
        'sample/report/report_haematology.xml',
        'sample/report/report_microbiology.xml',
        'sample/report/report_serology.xml',
        'sample/report/report_urine.xml',
        'sample/report/report_biochemistry.xml',
        'sample/report/report_stool.xml',
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
        'dashboards/hospital_dashboard_menu.xml',
        'dashboards/hospital_dashboard.xml',
        'expense/expense_view.xml',
        'expense/expense_pending_view.xml',
        'expense/expense_cancel_view.xml',
        'Group/report/report_group_layout.xml',
        'Group/report/group_print_menu.xml',
        'Diagnosis/report/report_diagnosis_layout.xml',
        'Diagnosis/report/diagnosis_print_menu.xml',
        'examine_entry/report/report_examine_entry_layout.xml',
        'examine_entry/report/examine_entry_print_menu.xml',
        'ward/wardform_view.xml',
        'discount/discount_view.xml',
        'discount/pending_discount_view.xml',
        'discount/approved_discount_view.xml',
        'discount/cancelled_discount_view.xml',
        'opd/opd_view.xml',
        'opd/opd_ticket_view.xml',
        'opd/report/opd_ticket_report.xml',
        'opd/report/opd_ticket_report_menu.xml',
        'admission/leih_admission_view.xml',
        'admission/leih_admission_activated_view.xml',
        'admission/leih_admission_released_view.xml',
        'admission/leih_admission_cancelled_view.xml',
        'admission/release/admission_release_view.xml',
        'admission/leih_emergency_view.xml',
        'admission/leih_emergency_activated_view.xml',
        'admission/leih_emergency_released_view.xml',
        'admission/payment/admission_payment_view.xml',
        'admission/report/admission_report_menu.xml',
        'admission/report/admission_report.xml',
        'money_receipt/money_receipt_view.xml',
        'bill_register/payment/bill_register_payment_view.xml',
        'cash_collection/cash_collection_view.xml',
        'cash_collection/cash_collection_pending_view.xml',
        'cash_collection/cash_collection_confirmed_view.xml',
        'cash_collection/cash_collection_cancelled_view.xml',
        'cash_collection/report/report_cc_collection.xml',
        'cash_collection/report/report_detail_component.xml',
        'discount/discount_category_view.xml',
        'discount/discount_configuration_view.xml',
        'discount/corporate_discount_view.xml',
        'commission/commission_view.xml',
        'commission/commission_configuration_view.xml',
        'commission/commission_calculation_view.xml',
        'commission/report/report_commission.xml',
        'commission/report/report_commission_menu.xml',
        'commission/commission_payment_view.xml',
        'appointment/appointment_booking_view.xml',
        'appointment/appointment_booking_paid_view.xml',
        'admission/payment_config/admission_payment_view.xml',
        'appointment/appointment_booking_view.xml',
        'appointment/appointment_payment/appointment_payment_view.xml',
        'appointment/appointment_report/appointment_report_menu.xml',
        'appointment/appointment_report/report_appointment.xml',
        'appointment/appointment_report/report_appointment.xml',
        'bill_register/investigation_payment/investigation_payment_view.xml',
        'optics/optics_sale_view.xml',
        'optics/payment/optics_sale_payment_view.xml',
        'optics/product_lens_view.xml',
        'optics/report/optics_report_menu.xml',
        'optics/report/report_optics_sale.xml',
        'inventory/inventory_requisition_view.xml',






    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'website': 'https://www.mufti.com'
}
