Batch input for Xero
--------------------

Need to create csv files containing:

  ContactName
    e.g. Jonathan Clark
    get from Access - a table with Name and Sage-Id
  Reference
    e.g. CLAJ
    get from Access
  InvoiceNumber
    Manual input, copy from row above
  InvoiceDate
    Manual input, ditto
  DueDate
    InvoiceDate plus 7
  Description
    From CoA plus extra text
  Quantity	
    Always 1
  UnitAmount
    From price list or manual
  AccountCode	
    From CoA
  TaxType	
    Alway No VAT
  TrackingName1
    Club
  TrackingOption1
    Unicorn or OUTC

So create tables for
  contacts
    reference
    name
    club
  coa
    code
    description
    type
    tax_code
  clubs
    name

