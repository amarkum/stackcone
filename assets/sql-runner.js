(function () {
  var SQLJS_VERSION = '1.10.3';
  var SQLJS_BASE = 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/' + SQLJS_VERSION + '/';

  // The lesson database. Every Run starts from this snapshot, so a DELETE in one
  // snippet never surprises the next one. The rows match the tables printed in
  // the lessons (Ada / Linus / Grace and their three orders).
  var SEED = [
    'PRAGMA foreign_keys = ON;',
    'CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT, age INTEGER, email TEXT UNIQUE, phone TEXT);',
    "INSERT INTO customers VALUES (1,'Ada','UK',36,'ada@example.com','+44 20 7946 0958')," +
      "(2,'Linus','FI',28,'linus@example.com',NULL)," +
      "(3,'Grace','US',45,'grace@example.com','+1 202 555 0143');",
    'CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id), total REAL, status TEXT);',
    "INSERT INTO orders VALUES (10,1,120.0,'paid'),(11,1,35.5,'paid'),(12,3,80.0,'refunded');",
    'CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);',
    "INSERT INTO people VALUES (1,'Ada',36),(2,'Linus',28),(3,'Zed',NULL);",
    'CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, manager_id INTEGER REFERENCES employees(id));',
    "INSERT INTO employees VALUES (1,'Grace',NULL),(2,'Ada',1),(3,'Linus',1);",
    'CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER);',
    "INSERT INTO products VALUES (1,'Keyboard',49.0,12),(2,'Monitor',180.0,4),(3,'Cable',9.5,120);",
    'CREATE TABLE accounts (id INTEGER PRIMARY KEY, owner TEXT, balance REAL);',
    "INSERT INTO accounts VALUES (1,'Ada',100),(2,'Linus',20);",
    'CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT);',
    "INSERT INTO users VALUES (1,'ada@example.com','Ada'),(2,'linus@example.com','Linus'),(3,'grace@example.com','Grace');"
  ].join('\n');

  function loadSqlJsScript() {
    return new Promise(function (resolve, reject) {
      if (typeof window.initSqlJs === 'function') {
        resolve(window.initSqlJs);
        return;
      }
      var existing = document.querySelector('script[data-sqljs]');
      if (existing) {
        existing.addEventListener('load', function () { resolve(window.initSqlJs); });
        existing.addEventListener('error', reject);
        return;
      }
      var script = document.createElement('script');
      script.src = SQLJS_BASE + 'sql-wasm.js';
      script.setAttribute('data-sqljs', 'true');
      script.onload = function () { resolve(window.initSqlJs); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function getSql() {
    if (!window.__stackconeSqlJsPromise) {
      window.__stackconeSqlJsPromise = loadSqlJsScript().then(function (initSqlJs) {
        return initSqlJs({ locateFile: function (file) { return SQLJS_BASE + file; } });
      });
    }
    return window.__stackconeSqlJsPromise;
  }

  // Lessons that teach CREATE TABLE / ALTER TABLE redefine things the seed already
  // has. Clear those out first so the snippet's own definition is the one that runs.
  function clearRedefined(db, code) {
    var re = /CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"[]?([A-Za-z_][\w$]*)[`"\]]?/gi;
    var names = [];
    var m;
    while ((m = re.exec(code))) names.push(m[1]);
    if (names.length) {
      // Seed tables reference each other, so a drop in the wrong order trips a
      // foreign key. Order does not matter with the checks off.
      db.run('PRAGMA foreign_keys = OFF;');
      names.forEach(function (name) {
        try { db.run('DROP TABLE IF EXISTS "' + name + '";'); } catch (e) { /* keep going */ }
      });
      db.run('PRAGMA foreign_keys = ON;');
    }

    var alter = /ALTER\s+TABLE\s+[`"[]?([A-Za-z_][\w$]*)[`"\]]?\s+ADD\s+(?:COLUMN\s+)?[`"[]?([A-Za-z_][\w$]*)/gi;
    while ((m = alter.exec(code))) {
      try { db.run('ALTER TABLE "' + m[1] + '" DROP COLUMN "' + m[2] + '";'); } catch (e) { /* column not there */ }
    }
  }

  // sqlite3_changes() covers only the last statement, so count real writes with
  // total_changes() on either side of the snippet.
  function totalChanges(db) {
    try {
      var r = db.exec('SELECT total_changes();');
      return r.length ? r[0].values[0][0] : 0;
    } catch (e) {
      return 0;
    }
  }

  function formatValue(v) {
    if (v === null || v === undefined) return 'NULL';
    if (v instanceof Uint8Array) return '<blob>';
    return String(v);
  }

  function renderTable(result) {
    var table = document.createElement('table');
    table.className = 'sql-result-table';

    var thead = document.createElement('thead');
    var hrow = document.createElement('tr');
    result.columns.forEach(function (col) {
      var th = document.createElement('th');
      th.textContent = col;
      hrow.appendChild(th);
    });
    thead.appendChild(hrow);
    table.appendChild(thead);

    var tbody = document.createElement('tbody');
    result.values.forEach(function (row) {
      var tr = document.createElement('tr');
      row.forEach(function (cell) {
        var td = document.createElement('td');
        var text = formatValue(cell);
        td.textContent = text;
        if (text === 'NULL') td.className = 'is-null';
        else if (typeof cell === 'number') td.className = 'is-num';
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return table;
  }

  function note(text) {
    var el = document.createElement('div');
    el.className = 'sql-result-note';
    el.textContent = text;
    return el;
  }

  function runSql(code, outputEl, runBtn) {
    if (!code || !code.trim()) {
      outputEl.textContent = '(no SQL to run)';
      outputEl.hidden = false;
      outputEl.classList.add('is-error');
      return Promise.resolve();
    }

    outputEl.hidden = false;
    outputEl.classList.remove('is-error');
    outputEl.textContent = 'Loading SQLite…';
    if (runBtn) {
      runBtn.disabled = true;
      runBtn.classList.add('is-loading');
    }

    return getSql()
      .then(function (SQL) {
        var db = new SQL.Database();
        db.run(SEED);
        clearRedefined(db, code);

        var frag = document.createDocumentFragment();
        var tables = 0;
        var baseline = totalChanges(db);
        try {
          var results = db.exec(code);
          results.forEach(function (result) {
            if (!result.columns || !result.columns.length) return;
            frag.appendChild(renderTable(result));
            tables++;
          });
          if (!tables) {
            var changes = totalChanges(db) - baseline;
            frag.appendChild(note(
              changes === 0 ? 'Statement ran. No rows returned.'
                : changes === 1 ? '1 row affected.'
                : changes + ' rows affected.'
            ));
          }
          outputEl.textContent = '';
          outputEl.classList.remove('is-error');
          outputEl.appendChild(frag);
        } catch (err) {
          outputEl.textContent = 'Error: ' + (err && err.message ? err.message : String(err));
          outputEl.classList.add('is-error');
        } finally {
          db.close();
        }
      })
      .catch(function (err) {
        outputEl.textContent = 'Failed to load SQLite: ' + (err.message || err);
        outputEl.classList.add('is-error');
      })
      .finally(function () {
        if (runBtn) {
          runBtn.disabled = false;
          runBtn.classList.remove('is-loading');
        }
      });
  }

  window.stackconeRunSql = runSql;
  window.stackconeSqlSeed = SEED;
})();
