class Help:

    topics = [
        {'item':'Updating Fuel Records', 'title':'How to update fuel', 'text':'help me!'},
        {'item':'Updating Service Records', 'title':'How to update service', 'text':'help me'},
        {'item':'Vehicle Management', 'title':'How to manage vehicles.', 'text':'help me'},
    ]

    def helpMenu(self):
        while True:
            # build the menu from the topics list
            menu = ''
            for topic in self.topics:
                menu += ('{}) {}\n'.format(self.topics.index(topic)+1, topic['item']))

            print('''\nChoose Help Topic:\n{}0) Back'''.format(menu))

            processed = False
            option = None
            option = input('Option? :')

            # check option is numeric
            if option and option.isnumeric():
                processed = True
                # convert option passed into topic index
                index = int(option) - 1

                if index == -1:
                    break;
                elif (index >= 0 and index < len(self.topics)):
                    print(self.topics[index]['title'])
                    print(self.topics[index]['text'])
                else:
                    processed = False

            if not processed:
                print('Invalid option [{0}]'.format(option))
