Function padCells()

With Application
    .ScreenUpdating = False
    .DisplayAlerts = False
    .EnableEvents = False
    .Calculation = xlCalculationManual
End With

On Error GoTo resetApp
    
Dim rng As Range
Dim rw As Range

    Set rng = Selection
    
    With rng.Rows
        .WrapText = True
        .AutoFit
    End With
    
    For Each rw In rng.Rows
        If rw.RowHeight >= 24 Then
            rw.RowHeight = rw.RowHeight + 10
        Else
            rw.RowHeight = 24
        End If
    Next

resetApp:
With Application
    .ScreenUpdating = True
    .DisplayAlerts = True
    .EnableEvents = True
    .Calculation = xlCalculationAutomatic
End With

End Function