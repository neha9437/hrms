# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID


class ServiceExperience(models.Model):
    _name = "service.experiance"
    _description = "Years of Experience"
    _rec_name = 'experiance'

    experiance = fields.Char(string='Experience', required=True, translate=True)
    
    
class ServiceDomain(models.Model):
    _name = "service.domain"
    _description = "Industry Domain"
    _rec_name = 'domain'

    domain = fields.Char(string='Name', required=True, translate=True)


# class ServiceCTC(models.Model):
#     _name = "service.ctc"
#     _description = "Current and expected CTC"
#     _rec_name = 'ctc'

#     ctc = fields.Char(string='CTC', required=True, translate=True)


# class ServiceDocuments(models.Model):
#     _name = "service.documents"
#     _description = "Uploading documents"
#     _rec_name = 'sub_document_id'

#     sub_document_id = fields.Many2one('service.sub.documents',string='Attach Documents')
#     datas = fields.Binary(attachment=True)
#     portal_master_id = fields.Many2one('service.portal.master', string='Portal')


# class ServiceSubDocuments(models.Model):
#     _name = "service.sub.documents"
#     _description = "Documents List"

#     name = fields.Char(string='Document Name', required=True, translate=True)
#     technical_name =  fields.Selection(
#         [('cv', 'cv'),
#         ('residence_proof', 'residence_proof'),
#         ('pan', 'pan'),
#         ('aadhar', 'aadhar'),
#         ('qualification_certificate', 'qualification_certificate'),
#         ('lc', 'lc'),
#         ('photo','photo'),
#         ('birth_certificate','birth_certificate'),
#         ('appraisal','appraisal'),
#         ('appointment','appointment'),
#         ('payslip','payslip'),
#         ('skill_certificate','skill_certificate')
#         ], required=True)


class ServicePfEsicNominee(models.Model):
    _name = "service.pf.esic.nominee"
    _description = "Nominees for candiate PF/ESIC"
    _rec_name = "nominee"

    nominee = fields.Char(string='Nominee', required=True, translate=True)
    percent = fields.Char(string='Percent', required=False, translate=True)


class Skillset(models.Model):
    _name = "skillset"
    _description = "Candidate Skills"

    name = fields.Char(string='Name', required=True, translate=True)


class CostCenter(models.Model):
    _name = "cost.center"
    _description = "Cost Centers"

    name = fields.Char(string='Nominee', required=True, translate=True)


class BankName(models.Model):
    _name = "bank.name"
    _description = "Bank Names"

    name = fields.Char(string='Bank Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)