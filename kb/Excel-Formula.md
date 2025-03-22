# Excel Formula

```shell
# C8 › Tab Data
=IF(RC1,CONCATENATE(TEXT(RC1,"000000000000"),"  ",LEFT(RC2 & REPT(" ",40),40),"  ",LEFT(RC3 &REPT(" ",15),15),"  ",LEFT(RC5 &REPT(" ",20),20),"  ",RC6),"")

# C10 › Custom Rule
=IF(RC1,CONCATENATE(
    IF(ISERROR(SEARCH("Health",RC8)),"","Divest/"),
    IF(ISERROR(SEARCH("Aviation",RC8)),"","GRE/"),
    IF(ISERROR(SEARCH("Vernova",RC8)),"","Convey/"),
RC2),"")

# C11 › Gossamer3 Access Script
=IF(RC1,LET(tab, REPT(" ",6),CONCATENATE(
    tab & "# ",RC[-4]," ",TEXT(RC1,"000000000000")," [",RC2,"] ",RC8,CHAR(10),
    IF(AND(ISNUMBER(SEARCH("GovCloud",RC[-4])),NOT(ISNUMBER(SEARCH("-commercial",RC[-9])))),
        tab & "- role_arn: arn:aws-us-gov:iam::",
        tab & "- role_arn: arn:aws:iam::"
    ),
    TEXT(RC1,"000000000000"),":role/cs/",IF(ISTEXT(RC9),RC9,"p-engineering"),CHAR(10),
    tab & "  profile: ",IF(ISTEXT(RC10),RC10,RC2)
)),"")

```


```shell
=IF(AND(COUNTIF(Scope!RC9, RC9), INDEX(Scope!C:C, MATCH(RC9, Scope!C:C, 0))="Verify"), TRUE, FALSE)
=IF(AND(COUNTIF(Scope!RC9, RC9), INDEX(Scope!C:C, MATCH(RC9, Scope!RC9, 0))="Verify"), TRUE, FALSE)
```

## Logical-Segregation Excel File
```shell
# Look for BU Segment
=IF(ISNA(VLOOKUP(RC9, Scope!R2C9:R1000C9, 1, FALSE)), "N", "Y")

=IF(AND(COUNTIF(Scope!RC9, RC9)), TRUE, FALSE)

# Summary!
# C5 › Row Index
=IF(RC6,ROW()-1,"")

# C6 › Summay Accounts
=SORT(UNIQUE(FILTER(ACCOUNT.DL!R2C1:R1000C1, ACCOUNT.DL!R2C1:R1000C1<>"")))

# C7 › Summay Accounts Name
=IF(RC6<>"", XLOOKUP(RC6, CMC!R2C1:R4000C1, CMC!R2C2:R4000C2, "External"),"")

# C8 › Summay DL Count
=IF(RC[-2], COUNTIF(ACCOUNT.DL!R2C1:R1000C1, RC[-2]),"")


# ACCOUNT.DL!
# ›  DL ACCOUNT
=IF(RC6<>"", NUMBERVALUE(RIGHT(RC6,12)),"")

# DL ACCOUNT BU
=IF(RC7<>"", XLOOKUP(RC7, CMC!R2C1:R4000C1,CMC!R2C6:R4000C6,"External"),"")


# DL.PM!
1. Filter IDM.DL! for `User Role` = `PrimaryManager`
2. Copy filtered `IDM.DL!` to `DL.PM!` to have `DL.PrimaryManager`

# Scope!
# C2 › Account Name
=IF(RC1,XLOOKUP(RC1,CMC!R2C1:R4000C1,CMC!R2C2:R4000C2),"")

# C4 › Status
=IF(RC1,XLOOKUP(RC1,CMC!R2C1:R4000C1,CMC!R2C4:R4000C4),"")

# C5 › Console
=IF(RC1,
  HYPERLINK(CONCATENATE(
    "https://signin",
    IF(AND(ISNUMBER(SEARCH("gov",RC2)),NOT(ISNUMBER(SEARCH("-commercial",RC2)))),
      ".amazonaws-us-gov",
      ".amazon"
    ),
  ".com/switchrole?account=",
  TEXT(RC1,"000000000000"),
  "&roleName=cs/p-engineering&displayName=",
  "cs/p-eng@",
  RC2
),RC1),"")

# C6 › SKU
=IF(RC1,XLOOKUP(RC1,CMC!R1C1:R4000C1,CMC!R1C5:R4000C5),"")

# C7 › Business Unit
=IF(RC1,XLOOKUP(RC1,CMC!R1C1:R4000C1,CMC!R1C6:R4000C6),"")

# R1C9 › Whitelist BU Segment
=CONCATENATE("Whitelist BU Segment (",TEXT(COUNTIF(R2C:R1000C,"<>"),"#,##0"),")")

# C10 › Action
# Drop-down list values for BU Whitelist BU Segment


# Disposition!
# R1C14 › Disposition (count)
=CONCATENATE("Disposition (",TEXT(COUNTIF(R2C:R1000C,"=Yes"),"#,##0"), ")")
# C14 › Disposition (count)
=IF(ISNA(VLOOKUP(RC9,Scope!R2C9:R1000C9, 1, FALSE)), IF(RC16="Yes", "Yes", ""), "")

# R1C15 › Verify (count)
=CONCATENATE("Verify (", TEXT(COUNTIF(R2C:R1000C,"=Verify"),"#,##0"), ")")
# C15 › Verify (count)
=IF(XLOOKUP(RC9, Scope!R2C9:R1000C9, Scope!R2C10:R1000C10)="Verify", "Verify", "")

# C16 › In Scope
=IF(ISNA(VLOOKUP(RC18,Scope!R2C1:R1000C1, 1, FALSE)), "", IF(RC9<>"", "Yes", ""))

# C17 › DL Account BU
=IF(ISNUMBER(VALUE(RIGHT(RC2, 12))), XLOOKUP(NUMBERVALUE(RIGHT(RC2,12)), CMC!R2C1:R4000C1, CMC!R2C6:R4000C6), "")

# C18 › DL Account
=IF(ISNUMBER(NUMBERVALUE(RIGHT(RC2,12))), XLOOKUP(NUMBERVALUE(RIGHT(RC2,12)), CMC!R2C1:R4000C1, CMC!R2C1:R4000C1),"")

# C19 › DL Account Name
=IF(ISNUMBER(NUMBERVALUE(RIGHT(RC2, 12))), XLOOKUP(NUMBERVALUE(RIGHT(RC2,12)), CMC!R2C1:R4000C1,CMC!R2C2:R4000C2), "")

# C20 › DL Manager
=IF(RC1<>"", XLOOKUP(RC1, DL.PM!R2C1:R1000C1, DL.PM!R2C8:R1000C8), "")

# C21 › DL Manager Name
=IF(RC20<>"", XLOOKUP(RC20, IDM.USER!R2C1:R5000C1, IDM.USER!R2C4:R5000C4))
```