'use strict';

var childProc = require('child_process'),
  path = require('path');

module.exports = function (grunt) {
  var cfg, optNoCompress, _;

  _ = grunt.util._;
  /* load configuration */
  cfg = grunt.file.readYAML('_config.yml');
  optNoCompress = grunt.option('no-compress');

  grunt.initConfig({
    jshint: {
      options: { jshintrc: '.jshintrc' },
      gruntfile: { src: 'Gruntfile.js' },
      config: { src: ['_config/vim_fanfou.js'] }
    },
    clean: [
      cfg.dest.cssMain,
      cfg.dest.jsMain,
      cfg.dest.htmlMain,
      'assets/fonts'
    ],
    concat: {
      css: {
        src: [
          cfg.mod.cssBootstrap,
          '_config/vim_fanfou.css'
        ],
        dest: cfg.dest.cssMain
      },
      js: {
        src: [
          cfg.mod.jsJQuery,
          cfg.mod.jsBootstrap,
          cfg.mod.jsLazyLoad,
          '_config/vim_fanfou.js',
          '_config/ganalytics.js'
        ],
        dest: cfg.dest.jsMain
      }
    },
    copy: {
      fonts: {
        expand: true,
        cwd: cfg.mod.dirBootstrap,
        src: [ 'fonts/**/*' ],
        dest: __dirname + '/assets'
      }
    },
    htmlmin: {
      dist: {
        options: { removeComments: true, collapseWhitespace: true },
        files: { 'index.html': 'index.html' }
      }
    },
    cssmin: { minify: { src: [ cfg.dest.cssMain ], dest: cfg.dest.cssMain } },
    uglify: { dist: { src: cfg.dest.jsMain, dest: cfg.dest.jsMain} },
    watch: {
      content: {
        files: [ 'index.md' ],
        tasks: [ 'makePages' ],
        options: { spawn: false }
      }
    },
    connect: {
      dist: {
        options: {
          port: cfg.util.servPort,
          debug: cfg.util.servDbg,
          base: __dirname
        }
      }
    },
    /* create site map */
    sitemap: {
      cwd: './',
      dest: 'sitemap.txt',
      site: 'http://xiongjia.github.io/vim-fanfou'
    },
    makePages: {
      pages: [ {src: 'index.md', dest: 'index.html'} ]
    }
  });

  /* load plugins */
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-htmlmin');
  grunt.loadNpmTasks('grunt-contrib-copy');

  /* sitemap task */
  grunt.registerTask('sitemap', 'create sitemap.txt', function () {
    var pages, pgCwd, dest, site, data;

    /* check options */
    grunt.config.requires('sitemap', 'sitemap.cwd',
      'sitemap.dest', 'sitemap.site');

    pgCwd = grunt.config.get('sitemap.cwd');
    dest = grunt.config.get('sitemap.dest');
    site = grunt.config.get('sitemap.site');
    grunt.log.writeln('creating sitemap. { cwd:%s, dest: %s, site: %s }',
      pgCwd, dest, site);

    /* save the sitemap to 'data' */
    pages = grunt.file.expand({cwd: pgCwd}, '*.html');
    data = '';
    grunt.util._.each(pages, function (pg) {
      data = data + grunt.util._.str.sprintf('%s/%s\n', site, pg);
    });
    /* write sitemap to dest file */
    grunt.file.write(dest, data);
  });

  /* make pages task */
  grunt.registerTask('makePages', 'make html pages', function () {
    var pages, tasks, done, htmlTemplate;

    grunt.config.requires('makePages', 'makePages.pages');
    pages = grunt.config.get('makePages.pages');
    grunt.log.writeln('Make pages: %j', pages);
    htmlTemplate = path.join(__dirname, '_config/html_home.tpl');

    function runPandoc(opts, callback) {
      var proc, procArgs, stdOut, stdErr;
      callback = callback || function () {};
      opts = opts || {};
      stdOut = '';
      stdErr = '';
      procArgs = [
        _.str.sprintf('--template=%s', htmlTemplate),
        '--toc',
        '-o', opts.html,
        opts.md
      ];
      grunt.log.writeln('pandoc %j', procArgs);
      proc = childProc.spawn('pandoc', procArgs,
        { cwd: __dirname, env: process.env });
      proc.on('exit', function (code) {
        var err;
        if (code !== 0) {
          grunt.log.writeln('pandoc exited with code %d', code);
          grunt.log.writeln('STDOUT:\n %s', stdOut);
          grunt.log.writeln('STDERR:\n %s', stdErr);
          err = new Error(_.str.sprintf('pandoc exited with code %d', code));
        }
        callback(err);
      });
      proc.stdout.on('data', function (data) { stdOut += data.toString(); });
      proc.stderr.on('data', function (data) { stdErr += data.toString(); });
    }

    tasks = [];
    _.each(pages, function (pg) {
      if (!pg || !pg.dest || !pg.src) {
        return;
      }
      grunt.log.writeln('%s ==> %s', pg.src, pg.dest);
      tasks.push(function (callback) {
        runPandoc({ md: pg.src, html: pg.dest }, callback);
      });
    });

    /* start pandoc tasks */
    done = this.async();
    require('async').parallel(tasks, function (err) {
      grunt.log.writeln('All pages have been created');
      done(err);
    });
  });
 
  /* alias */
  grunt.registerTask('pack',
    optNoCompress ? 'Make Pages (no compress)' : 'Make Pages',
    optNoCompress ?
      ['jshint', 'makePages'] :
      ['jshint', 'makePages', 'htmlmin']);

  grunt.registerTask('initPack',
    optNoCompress ?  'Export all files (no compress)' : 'Export all files',
    optNoCompress ?
      ['clean', 'jshint', 'concat', 'copy', 'pack', 'sitemap' ] :
      ['clean', 'jshint', 'concat', 'copy', 'pack', 'uglify', 'cssmin', 'sitemap' ]);

  grunt.registerTask('serv', 'Launch local test server',
    ['connect', 'watch']);
  grunt.registerTask('server', ['serv']);

  /* default task */
  grunt.registerTask('default', ['pack']);
};

