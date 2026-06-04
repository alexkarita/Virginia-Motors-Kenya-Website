from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os, hashlib, secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DB = 'showroom.db'

# ══════════════════════════════════════════════════════════════════
#  ✏️  VIRGINIA — FILL IN YOUR REAL DETAILS BELOW BEFORE GOING LIVE
# ══════════════════════════════════════════════════════════════════
ADMIN_EMAIL       = 'Wanguvirginia1@gmail.com'
ADMIN_PASSWORD    = 'virginia2025'
VIRGINIA_WHATSAPP = '254707394750'
VIRGINIA_PHONE    = '0707 394 750'
VIRGINIA_EMAIL    = 'Wanguvirginia1@gmail.com'
# ══════════════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    return session.get('is_admin', False)

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                price INTEGER NOT NULL,
                mileage INTEGER DEFAULT 0,
                fuel_type TEXT,
                transmission TEXT,
                body_type TEXT,
                color TEXT,
                description TEXT,
                condition TEXT DEFAULT 'Used',
                location TEXT,
                images TEXT DEFAULT '',
                featured INTEGER DEFAULT 0,
                sold INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()

# ── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    featured = db.execute("SELECT * FROM cars WHERE featured=1 AND sold=0 ORDER BY created_at DESC LIMIT 6").fetchall()
    recent   = db.execute("SELECT * FROM cars WHERE sold=0 ORDER BY created_at DESC LIMIT 8").fetchall()
    stats = {
        'total':  db.execute("SELECT COUNT(*) FROM cars WHERE sold=0").fetchone()[0],
        'brands': db.execute("SELECT COUNT(DISTINCT brand) FROM cars").fetchone()[0],
        'sold':   db.execute("SELECT COUNT(*) FROM cars WHERE sold=1").fetchone()[0],
    }
    contact = {'whatsapp': VIRGINIA_WHATSAPP, 'phone': VIRGINIA_PHONE, 'email': VIRGINIA_EMAIL}
    return render_template('index.html', featured=featured, recent=recent, stats=stats, contact=contact)

@app.route('/cars')
def cars():
    db = get_db()
    q     = request.args.get('q','')
    brand = request.args.get('brand','')
    fuel  = request.args.get('fuel','')
    trans = request.args.get('trans','')
    body  = request.args.get('body','')
    cond  = request.args.get('cond','')
    min_p = request.args.get('min_p', 0, type=int)
    max_p = request.args.get('max_p', 999999999, type=int)
    sort  = request.args.get('sort', 'newest')

    order = {'newest':'created_at DESC','price_asc':'price ASC','price_desc':'price DESC','mileage':'mileage ASC'}.get(sort,'created_at DESC')
    sql = "SELECT * FROM cars WHERE sold=0 "
    params = []
    if q:     sql += " AND (title LIKE ? OR brand LIKE ? OR model LIKE ?)"; params += [f'%{q}%']*3
    if brand: sql += " AND brand=?"; params.append(brand)
    if fuel:  sql += " AND fuel_type=?"; params.append(fuel)
    if trans: sql += " AND transmission=?"; params.append(trans)
    if body:  sql += " AND body_type=?"; params.append(body)
    if cond:  sql += " AND condition=?"; params.append(cond)
    sql += " AND price BETWEEN ? AND ?"; params += [min_p, max_p]
    sql += f" ORDER BY {order}"

    car_list = db.execute(sql, params).fetchall()
    brands   = [r[0] for r in db.execute("SELECT DISTINCT brand FROM cars ORDER BY brand").fetchall()]
    contact  = {'whatsapp': VIRGINIA_WHATSAPP}
    return render_template('cars.html', cars=car_list, brands=brands,
                           q=q, brand=brand, fuel=fuel, trans=trans,
                           body=body, cond=cond, sort=sort, min_p=min_p, max_p=max_p,
                           contact=contact)

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    db  = get_db()
    car = db.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    if not car: return redirect(url_for('cars'))
    db.execute("UPDATE cars SET views=views+1 WHERE id=?", (car_id,))
    db.commit()
    related  = db.execute("SELECT * FROM cars WHERE brand=? AND id!=? AND sold=0 LIMIT 4", (car['brand'], car_id)).fetchall()
    contact  = {'whatsapp': VIRGINIA_WHATSAPP, 'phone': VIRGINIA_PHONE, 'email': VIRGINIA_EMAIL}
    return render_template('car_detail.html', car=car, related=related, contact=contact)

@app.route('/contact')
def contact():
    contact = {'whatsapp': VIRGINIA_WHATSAPP, 'phone': VIRGINIA_PHONE, 'email': VIRGINIA_EMAIL}
    return render_template('contact.html', contact=contact)

# ── ADMIN ROUTES ──────────────────────────────────────────────────────────────

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if is_admin(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        if request.form['email'] == ADMIN_EMAIL and request.form['password'] == ADMIN_PASSWORD:
            session['is_admin'] = True
            flash('Welcome back, Virginia! 👋', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Wrong email or password.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin(): return redirect(url_for('admin_login'))
    db   = get_db()
    all_cars = db.execute("SELECT * FROM cars ORDER BY created_at DESC").fetchall()
    stats = {
        'active': db.execute("SELECT COUNT(*) FROM cars WHERE sold=0").fetchone()[0],
        'sold':   db.execute("SELECT COUNT(*) FROM cars WHERE sold=1").fetchone()[0],
        'views':  db.execute("SELECT SUM(views) FROM cars").fetchone()[0] or 0,
        'featured': db.execute("SELECT COUNT(*) FROM cars WHERE featured=1").fetchone()[0],
    }
    return render_template('admin_dashboard.html', cars=all_cars, stats=stats)

@app.route('/admin/add', methods=['GET','POST'])
def admin_add():
    if not is_admin(): return redirect(url_for('admin_login'))
    if request.method == 'POST':
        db    = get_db()
        files = request.files.getlist('images')
        imgs  = []
        for f in files[:8]:
            if f and allowed_file(f.filename):
                fn = secure_filename(f'{secrets.token_hex(8)}_{f.filename}')
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                imgs.append(fn)
        db.execute('''INSERT INTO cars (title,brand,model,year,price,mileage,fuel_type,
                      transmission,body_type,color,description,condition,location,images,featured)
                      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            request.form['title'], request.form['brand'], request.form['model'],
            int(request.form['year']), int(request.form['price']),
            request.form.get('mileage') or 0, request.form['fuel_type'],
            request.form['transmission'], request.form['body_type'],
            request.form.get('color',''), request.form.get('description',''),
            request.form.get('condition','Used'), request.form.get('location',''),
            ','.join(imgs), 1 if request.form.get('featured') else 0
        ))
        db.commit()
        flash('Car listed successfully! 🎉', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_add.html')

@app.route('/admin/edit/<int:car_id>', methods=['GET','POST'])
def admin_edit(car_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    db  = get_db()
    car = db.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    if not car: return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        # Handle new image uploads
        files    = request.files.getlist('new_images')
        new_imgs = []
        for f in files[:8]:
            if f and f.filename and allowed_file(f.filename):
                fn = secure_filename(f'{secrets.token_hex(8)}_{f.filename}')
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                new_imgs.append(fn)
        # Keep existing images unless removed
        keep    = request.form.get('keep_images','')
        all_imgs = [i for i in keep.split(',') if i] + new_imgs
        db.execute('''UPDATE cars SET title=?,brand=?,model=?,year=?,price=?,mileage=?,
                      fuel_type=?,transmission=?,body_type=?,color=?,description=?,
                      condition=?,location=?,images=?,featured=?,sold=? WHERE id=?''', (
            request.form['title'], request.form['brand'], request.form['model'],
            int(request.form['year']), int(request.form['price']),
            request.form.get('mileage') or 0, request.form['fuel_type'],
            request.form['transmission'], request.form['body_type'],
            request.form.get('color',''), request.form.get('description',''),
            request.form.get('condition','Used'), request.form.get('location',''),
            ','.join(all_imgs),
            1 if request.form.get('featured') else 0,
            1 if request.form.get('sold') else 0,
            car_id
        ))
        db.commit()
        flash('Car updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_edit.html', car=car)

@app.route('/admin/delete/<int:car_id>')
def admin_delete(car_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    get_db().execute("DELETE FROM cars WHERE id=?", (car_id,))
    get_db().commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_sold/<int:car_id>')
def toggle_sold(car_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    db  = get_db()
    cur = db.execute("SELECT sold FROM cars WHERE id=?", (car_id,)).fetchone()['sold']
    db.execute("UPDATE cars SET sold=? WHERE id=?", (0 if cur else 1, car_id))
    db.commit()
    flash('Status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_featured/<int:car_id>')
def toggle_featured(car_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    db  = get_db()
    cur = db.execute("SELECT featured FROM cars WHERE id=?", (car_id,)).fetchone()['featured']
    db.execute("UPDATE cars SET featured=? WHERE id=?", (0 if cur else 1, car_id))
    db.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

# ── FILTERS ───────────────────────────────────────────────────────────────────

@app.template_filter('format_price')
def format_price(v):
    return f"KES {int(v):,}"

@app.template_filter('format_mileage')
def format_mileage(v):
    return f"{int(v):,} km" if v else 'N/A'

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)