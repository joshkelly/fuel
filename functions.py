import getopt, sys, datetime, sqlite3, string, time, math
import dbi
from cli import CLI
from operator import itemgetter

cur=None
conn=None
debug=False
ltr_gal_conv = 4.54609 # liters in an imperial gallon
vehicles = []
fuel = []
summaries = []

vrec = {'vehicle_id' : None, 'reg_no' :'', 'make' :'', 'model' :'', 'year' : 0, 'purchase_price' : 0, 'purchase_date' :'', 'fuel_cap' : 0, 'fuel_type' :'', 'oil_cap' : 0, 'oil_type' :'', 'tyre_front_cap' : 0, 'tyre_front_type' :'', 'tyre_rear_cap':'', 'tyre_rear_type':'', 'notes' :''}
frec = {'fuel_id':None, 'vehicle_id':0, 'date':'', 'litres':0, 'ppl':0, 'trip':0, 'odo':0, 'cost':0, 'mpg':0, 'notes':''}
srec = {'service_id':None, 'vehicle_id':0, 'date':'', 'cost':0, 'odo':0, 'item':'', 'notes':''}

forms={
    'vehicle':['reg_no', 'make', 'model', 'year', 'purchase_price', 'purchase_date', 'fuel_cap', 'fuel_type', 'oil_cap', 'oil_type', 'tyre_front_cap', 'tyre_rear_type', 'tyre_rear_cap', 'tyre_rear_type','notes'],
    'fuel':['vehicle_id', 'date', 'litres', 'ppl', 'trip', 'odo', 'cost', 'notes'],
    'service':['date', 'cost', 'odo', 'item', 'notes']
}

scalex=700
scaley=500
svg = '''
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="800" height="600">
	<text x="400" y="25" text-anchor="middle" fill="black" stroke="none" font-weight='normal'>Fuel Economy for {0}</text>
	<line stroke="black" x1="50" y1="550" x2="750" y2="550"/><!-- xaxis 700 wide-->
	<line stroke="black" x1="50" y1="50"  x2="50"  y2="550"/><!-- yaxis 500 tall -->
    {1}
</svg>
'''

def time_now():
    return time.time()

def to_date(secs):
    '''Convert seconds to date string'''
    return time.strftime("%Y/%m/%d", time.localtime(secs))

def to_seconds(date):
    '''Convert date string to seconds'''
    return time.mktime(time.strptime(date, "%Y/%m/%d"))


def update_vehicle(vehicle):
    '''
    Modify a vehicle record
    '''
    save('vehicles', vehicle)


def remove_vehicle(vehicle):
    '''
    Remove vehicle from data
    '''
    cur.execute('delete from vehicles where reg_no="{0}"'.format(vehicle['reg_no']))
    conn.commit()
    load()

def load():
    '''
    Load data from DB.
    Establish connection and get cursor.
    '''
    global conn, cur, fuel, vehicles, service
    if conn == None:
        conn = dbi.init()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    # get data, copy to editable dictionary, inform user of record count
    cur.execute('select * from fuel')
    fuel = [dict(row) for row in cur]
    print('Loaded {} fuel records.'.format(len(fuel)))
    
    cur.execute('select * from vehicles')
    vehicles = [dict(row) for row in cur]
    print('Loaded {} vehicles.'.format(len(vehicles)))

    cur.execute('select * from service')
    service = [dict(row) for row in cur]
    print('Loaded {} service records.'.format(len(service)))

def save(tbl, rec):
    '''
    Save data to DB.
    Check `tbl` to handle `rec` properly 
    Reload all data from db.
    '''
    global conn, cur
    if tbl == 'fuel':
        # fuel_id integer, primary key
        # vehicle_id integer, use reg as look up into vdata
        # date text, map to date
        # litres real, map to 'litres'
        # ppl real, map to 'ppl'
        # trip real, map to 'trip'
        # odo integer, map to 'odo'
        # cost real, calculate as (ppl * litres), store to 2 d.p.
        # mpg real, map to 'mpg'
        # notes text, map to 'notes'
        cur.execute("insert or replace into fuel values (?,?,?,?,?,?,?,?,?,?)", [rec['fuel_id'], rec['vehicle_id'], rec['date'], rec['litres'], rec['ppl'], rec['trip'], rec['odo'], rec['cost'], rec['mpg'], rec['notes']])
        conn.commit()
    elif tbl == 'vehicles':
        # vehicle_id integer, no data, unique key
        # reg_no text, map to 'reg'
        # make text, map to 'make' 
        # model text, map to 'model'
        # year integer, map to 'year'
        # purchase_price real, no data, 0
        # purchase_date text, no data, 2013/08/16
        # fuel_cap real, map to 'ftc'
        # fuel_type text, no data, ''
        # oil_cap real,no data, 0
        # oil_type text, no data, ''
        # tyre_front_cap real,no data, 0
        # tyre_front_type text,no data, ''
        # tyre_rear_cap real,no data, 0
        # tyre_rear_type text,no data, ''
        # notes text, no data, ''
        cur.execute('insert or replace into vehicles values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [rec['vehicle_id'], rec['reg_no'], rec['make'], rec['model'], rec['year'], rec['purchase_price'], rec['purchase_date'], rec['fuel_cap'], rec['fuel_type'], rec['oil_cap'], rec['oil_type'], rec['tyre_front_cap'], rec['tyre_front_type'], rec['tyre_rear_cap'], rec['tyre_rear_type'], rec['notes']])
        conn.commit()
    elif tbl == 'service':
        # service_id integer, primary key and index
        # vehicle_id integer, fkey into vehicles
        # date text, date of service item
        # cost real, cost of item
        # odo integer, optional
        # item text, description of item
        # notes text, free text
        cur.execute('insert or replace into service values (?,?,?,?,?,?,?)', [rec['service_id'], rec['vehicle_id'], rec['date'], rec['cost'], rec['odo'], rec['item'], rec['notes']])
        conn.commit()
    else:
        print('Unrecognised table:', tbl)

    load()

def update_fuel(vehicle, record):
    '''
    Create or update a fuel record

    @return calculated mpg
    '''
    # caclulate the mpg
    calc_mpg(record)

    # update database
    save('fuel', record)

    # generate graph
    fuel_graph(vehicle)

    return record['mpg']

def update_service(service):
    '''
    Modify a service record
    '''
    save('service', service)

def calc_mpg(record):
    '''
    Calculate MPG for record.
    '''
    record['gallons'] = record['litres']/ltr_gal_conv
    record['mpg'] = record['trip']/record['gallons']

def last_fuel(vehicle):
    '''
    Get last record for this vehicle
    '''
    curr = None
    for record in fuel:
        if record['vehicle_id'] == vehicle['vehicle_id']:
            if curr == None:
                curr = record
            else:
                if curr['date'] < record['date']:
                    curr = record

    return curr

def get_summary(vehicle):
    '''
    Create/update summary fuel for a vehicle
    if no vehicle passed, prompt user to choose, calculate, save and display results
    if vehicle passed, calculate, save and return results
    '''
    sum_rec = {
        'mpg':{'avg':0.0, 'min':float('inf'), 'max':0.0},
        'trip':{'avg':0.0, 'min':float('inf'), 'max':0.0, 'total':0.0},
        'ppl':{'avg':0.0, 'min':float('inf'), 'max':0.0},
        'cost':{'avg':0.0, 'min':float('inf'), 'max':0.0, 'total':0.0}
    }

    sql = "select min({0}) as min, max({0}) as max, avg({0}) as avg, sum({0}) as sum from fuel where vehicle_id='{1}'"

    for s in sum_rec:
        cur.execute(sql.format(s, vehicle['vehicle_id']))
        recs = [dict(row) for row in cur]
        sum_rec[s]['avg']=recs[0]['avg']
        sum_rec[s]['min']=recs[0]['min']
        sum_rec[s]['max']=recs[0]['max']
        if s == 'trip' or s == 'cost':
            sum_rec[s]['total']=recs[0]['sum']

    sum_rec['reg_no']=vehicle['reg_no']
    
    sql = "select sum(cost) from service where vehicle_id='{0}'"
    cur.execute(sql.format(vehicle['vehicle_id']))
    sum_rec['cost']
    return sum_rec

def predict(vehicle):
    '''
    Based on chosen vehicle's average MPG, calculate max distance travelable
    '''
    sum_rec = get_summary(vehicle)

    ftcg = vehicle['fuel_cap'] / ltr_gal_conv
    return sum_rec['mpg']['avg'] * ftcg

def get_service(vehicle):
    '''get date-sorted list of fuel for the selected vehicle'''
    cur.execute('select * from service where vehicle_id="{0}" order by date asc'.format(vehicle['vehicle_id']))
    return [dict(row) for row in cur]

def get_fuel(vehicle):
    '''
    Get all fuel record this vehicle
    '''
    # extract fuel for this vehicle, store in temporary
    mpg_min=99999999
    mpg_max = 0
    recs = []
    num = 0
    dmin=999999999999
    dmax=0
    drange = 0
    for r in fuel:
        if r['vehicle_id'] == vehicle['vehicle_id']:
            m = r['mpg']
            dmax = max(dmax, r['date'])
            dmin = min(dmin, r['date'])
            mpg_max = max(mpg_max, m)
            mpg_min = min(mpg_min, m)

            recs.append(r)
            num += 1

    drange = dmax - dmin
    mpg_range = mpg_max - mpg_min
    recs = sorted(recs, key=itemgetter('date'))
    return recs

def fuel_graph(vehicle):
    '''
    For a vehicle, create an SVG graph showing the MPG over time.
    Include average MPG.
    '''
    global fuel
    sum_rec = get_summary(vehicle)
    mpg_avg = sum_rec['mpg']['avg']
    mpg_min=99999999
    mpg_max = 0

    # extract fuel for this vehicle, store in temporary
    recs = []
    num = 0
    dmin=999999999999
    dmax=0
    drange = 0
    for r in fuel:
        if r['vehicle_id'] == vehicle['vehicle_id']:
            dmax = max(dmax, r['date'])
            dmin = min(dmin, r['date'])
            mpg_max = max(mpg_max, r['mpg'])
            mpg_min = min(mpg_min, r['mpg'])

            recs.append(r)
            num += 1

    if len(recs) == 0:
        return
    drange = dmax - dmin

    # correct y axis
    mpg_max = math.ceil(mpg_max/10) * 10
    mpg_min = math.floor(mpg_min/10) * 10

    mpg_range = mpg_max - mpg_min
    newlist = sorted(recs, key=itemgetter('date'))

    inner_svg = ''

    # create ticks along axes
    tx_dist = scalex / 10 # 10 ticks on the axis
    ty_dist = scaley / 10 # 10 ticks on the axis
    offset=50
    for i in range(num+1):
        #print(i, num)
        tx = i * tx_dist
        ty = i * ty_dist
        x = tx + 50
        inner_svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="grey"/>\n'.format(x, 550, x, 560)
        y = ty + 50
        inner_svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="grey"/>\n'.format(40, y, 50, y)

        tx/=scalex
        tx*=drange
        tx+=dmin
        inner_svg += '<text x="{}" y="{}" text-anchor="middle" font-size="8" fill="black" stroke="none">{}</text>\n'.format(x, 575, to_date(tx))

        ty/=scaley
        ty*=mpg_range
        ty=mpg_max-ty
        inner_svg += '<text x="{}" y="{}" text-anchor="middle" font-size="8" fill="black" stroke="none">{}</text>\n'.format(40,y,ty)

    yscale = mpg_max
    xscale = dmax

    path = None
    x=None
    y=None
    points='<g id="points">'
    for r in newlist:
        x=r['date']
        y=r['mpg']

        # generate x coordinate
        x = (dmax - x) / drange
        x = scalex - (scalex * x)
        x += 50

        # generate y coordinate
        y = (mpg_max - y) / mpg_range
        y *= scaley
        y += 50

        inner_svg += '<circle cx="{:.2f}" cy="{:.2f}" r="2" fill="black"/>'.format(x,y)

        if path == None:
            path = 'M{:.2f},{:.2f}'
        else:
            path += ' L{:.2f},{:.2f}'
        path=path.format(x,y)

        y -= 5
        points += '<text x="{:.2f}" y="{:.2f}" text-anchor="middle" font-size="10" stroke="none" fill="black">{:.2f}</text>'.format(x,y,r['mpg'])

    inner_svg += '<path d="{}" fill="none" stroke="red" stroke-width="0.5"/>'.format(path)
    points+='</g>'
    inner_svg+=points

    # where does the average line go?
    y = mpg_max - mpg_avg
    y /= mpg_range
    y *= scaley
    y += 50
    inner_svg += '<line x1="50" y1="{0}" x2="750" y2="{0}" stroke="grey"/>\n'.format(y)
    inner_svg += '<text x="755" y="{}" dominant-baseline="central" font-size="10" stroke="none" fill="blue">Avg. {:.2f}</text>'.format(y,mpg_avg)

    #print(inner_svg)
    svg_fname = 'mpg-{}.svg'.format(vehicle['reg_no'])
    f = open(svg_fname, 'w')
    f.write(svg.format(vehicle['reg_no'], inner_svg)+'\n')
    f.close()
    print('File at ',svg_fname)

def vehicle_menu():
    '''
    Manage vehicles sub-main_menu
    '''
    print('''Vehicles:
    1) Add
    2) Edit
    3) List
    4) Remove
    0) Back to Main Menu
    ''')
    processed = False
    option = None
    option = input('Option? :')

    if not option:
        vehicle_menu()

    # check option is numeric
    if option.isnumeric():
        processed = True
        option = int(option)

        if option == 0:
            main_menu()
        elif option == 1:
            add_vehicle()
        elif option == 2:
            edit_vehicle()
        elif option == 3:
            list_vehicles()
        elif option == 4:
            remove_vehicle()
        else:
            processed = False

    if not processed:
        print('Invalid option [{0}]'.format(option))
        vehicle_menu()

def exit():
    '''
    Stuff to do at shutdown
    
    Close DBI
    '''
    dbi.close()

def index():
    '''Create index page for graph links'''
    global vehicles

    html = '''<html>
    <head>
    <title>Fuel Economy and Service Records</title>
    </head>
    <body>
    <h1>Fuel Economy and Service Records</h1>
    {0}
    </body>
    </html>
    '''
    links = ''
    link = '''<a href="mpg-{0}.svg">Graph for {0}</a><p/>'''
    for v in vehicles:
        links+=link.format(v['reg_no'])
    f = open('index.html', 'w')
    f.write(html.format(links))
    f.close()
