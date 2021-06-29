from flask_assets import Bundle

app_css = Bundle('app.scss', filters='scss', output='styles/app.css')
search_request_css = Bundle('search_request.css', output='styles/search_request.css')

app_js = Bundle('app.js', filters='jsmin', output='scripts/app.js')
multidatespicker_js = Bundle('multidatespicker.js',
                             filters='jsmin',
                             output='scripts/multidatespicker.js')
search_request_js = Bundle('search_request.js',
                             filters='jsmin',
                             output='scripts/search_request.js')

vendor_css = Bundle('vendor/semantic.min.css', output='styles/vendor.css')

vendor_js = Bundle('vendor/jquery.min.js',
                   'vendor/semantic.min.js',
                   'vendor/tablesort.min.js',
                   'vendor/zxcvbn.js',
                   filters='jsmin',
                   output='scripts/vendor.js')
