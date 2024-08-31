Line Chart Field
================

Provides a field widget that displays a one to many relationship as a
line chart.

Example
-------

``` html
<field name="burndown_ids"
       style="width: 100%"
       widget="line_chart"
       options="{
           'chartOptions': {
               'legend': {
                   'display': False
               },
               'animation': False
           },
           'dataFields': ['date', 'planned_hours', 'available_hours'],
           'datasetOptions': {
               'date': {
                   'type': 'date'
               },
               'planned_hours': {
                  In  'borderColor': 'red'
               },
               'available_hours': {
                   'borderColor': 'blue'
               }
           }
       }"/>
```

 - The field (burndown_ids in this case) must be of type one to many.
 - Set the widget attribute to line_chart.
 - Use the options attribute to configure the chart.
   - chartOptions get forwarded to the Chart constructors options field. Default
     values are as follows:
     ```json
     {
        responsieve: true,
        maintainAspectRatio: false,
        legend: {
            display: true,
        },
        animation: {},
     }
     ```
   - dataFields: list of data ranges. The first one will be used as the X axis
     values, the rest will be plotted.
   - datasetOptions: use this field to set specific options for each data set as
     required by the Chart library. The type attribute is special in this regard:
     it defines the Odoo data type of the field (char by default) and can be used
     to customize its rendering. In the example the widget will render the X
     axis labels as localized date strings.
