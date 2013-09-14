class Help:

    topics = [
        {
            'item':'Vehicle Management', 
            'title':'Managing your vehicles.', 
            'text':'Select the `Vehicle Management` option to add/edit/list and remove vehicles.'
        },
        {
            'item':'Updating Fuel Records', 
            'title':'How to add/edit fuel records.', 
            'text':'Select `Add Fuel` to add a new record.|Choose a vehicle, then add details as requested.|To edit an existing record, select `Edit Record`.'
        },
        {
            'item':'Updating Service Records', 
            'title':'How to add/edit service records', 
            'text':'Select `Add Service` to add a new record.|Choose a vehicle, then add details as requested.|To edit an existing record, select `Edit Service`.'
        },
        {
            'item':'Summary and Prediction', 
            'title':'Summary and Prediction', 
            'text':'Select summary to see a break down of running costs, min/max/averages of vehicle data and costs per mile.|Select prediction for a range estimate of the selected vehicle.'

        },
        {
            'item':'Graphs', 
            'title':'Graphs', 
            'text':'Each time a fuel record is added or updated, a graph is created. See `index.html`'
        },
        {
            'item':'Data Storage', 
            'title':'Data Storage', 
            'text':'All data is store in a sqlite3 database file call `ldc_fuel.db`'
        },
    ]

    def helpTopics(self):
        return self.topics

