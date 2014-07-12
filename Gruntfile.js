'use strict';

var childProc = require('child_process');

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
    clean: [ cfg.dest.cssMain, cfg.dest.jsMain, cfg.dest.htmlMain ],
    concat: {
      js: {
        src: [
          cfg.mod.jsJQuery,
          '_config/vim_fanfou.js'
        ],
        dest: cfg.dest.jsMain
      }
    },
    uglify: { dist: { src: cfg.dest.jsMain, dest: cfg.dest.jsMain} },
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

  /* make pages task */
  grunt.registerTask('makePages', 'make html pages', function () {
    var pages, tasks, done;

    grunt.config.requires('makePages', 'makePages.pages');
    pages = grunt.config.get('makePages.pages');
    grunt.log.writeln('Make pages: %j', pages);

    function runPandoc(opts, callback) {
      var proc, procArgs, stdOut, stdErr;
      callback = callback || function () {};
      opts = opts || {};
      stdOut = '';
      stdErr = '';
      procArgs = ['-o', opts.html, opts.md];
      grunt.log.writeln('pandoc %j', procArgs);
      proc = childProc.spawn('pandoc', procArgs);
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
  grunt.registerTask('initPack',
    optNoCompress ?
      'Export all files (no compress)' : 'Export all files',
    optNoCompress ?
      ['clean', 'jshint', 'concat' ] :
      ['clean', 'jshint', 'concat' ]);

  grunt.registerTask('pack', ['jshint', 'makePages']);

  /* default task */
  grunt.registerTask('default', ['pack']);
};

