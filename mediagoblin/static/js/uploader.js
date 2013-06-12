(function (factory) {
    'use strict';
    if (typeof define === 'function' && define.amd) {
        define([
            'jquery',
            'tmpl',
            'load-image',
            './jquery.fileupload-fp'
        ], factory);
    } else {
        factory(
            window.jQuery,
            window.tmpl,
            window.loadImage
        );
    }
}(function ($, tmpl, loadImage) {
    'use strict';
    $.widget('blueimp.fileupload', $.blueimp.fileupload, {

        options: {
            //autoUpload: false,
            //maxNumberOfFiles: undefined,
            //maxFileSize: undefined,
            //minFileSize: undefined,
            //previewSourceFileTypes: /^image\/(gif|jpeg|png)$/,
            //previewSourceMaxFileSize: 5000000, // 5MB
            //previewMaxWidth: 80,
            //previewMaxHeight: 80,
            //previewAsCanvas: true,
            //uploadTemplateId: 'template-upload',
            //downloadTemplateId: 'template-download',
            //filesContainer: undefined,
        },

        _initButtonBarEventHandlers: function () {
            var fileUploadButtonBar = this.element.find('.button_form'),
                filesList = this.options.filesContainer;
            console.log(filesList.find('.template-upload'));
            this._on(fileUploadButtonBar, {
                click: function (e) {
                    e.preventDefault();
                    console.log($('.template-upload').data('data'));
                    $('.template-upload').each(function () {
                      var data = $(this).data('data');
                      if (data && data.submit && !data.jqXHR) {
                        data.submit()
                      }
                    });
                    console.log('done');
                }
            });

        },

        _destroyButtonBarEventHandlers: function () {
            this._off(
                this.element.find('.button_form button'),
                'click'
            );
            this._off(
                this.element.find('.button_form .toggle'),
                'change.'
            );
        },

        _renderExtendedProgress: function (data) {
            return this._formatBitrate(data.bitrate) + ' | ' +
                this._formatTime(
                    (data.total - data.loaded) * 8 / data.bitrate
                ) + ' | ' +
                this._formatPercentage(
                    data.loaded / data.total
                ) + ' | Uploading files... ' +
                (this._finishedUploads.length + this._sending) + '/' +
                (this._active + this._finishedUploads.length)
        },

        _transition: function (node) {
            var dfd = $.Deferred();
            if ($.support.transition && node.hasClass('fade')) {
                node.bind(
                    $.support.transition.end,
                    function (e) {
                        // Make sure we don't respond to other transitions events
                        // in the container element, e.g. from button elements:
                        if (e.target === node[0]) {
                            node.unbind($.support.transition.end);
                            dfd.resolveWith(node);
                        }
                    }
                ).fadeToggle();
            } else {
                node.fadeToggle();
                dfd.resolveWith(node);
            }
            return dfd;
        },
/*       // Callback for uploads start, equivalent to the global ajaxStart event:
       start: function (e) {
           var that = $(this).data('blueimp-fileupload') ||
                   $(this).data('fileupload');
           that._resetFinishedDeferreds();
           that._transition($(this).find('.progress'));
           that._transition($(this).find('.fileupload-progress')).done(
               function () {
                   that._trigger('started', e);
               }
           );
       }*/

    });

}));


$(function () {
    $('#fileupload').fileupload({
      sequentialUploads: true,
/*          start: function (e, data){
        $('.bar').innerHTML = "Upload file " + d
      },*/
/*        stop: function (e, data){
      console.log(data);
      console.log(e.total);
      console.log('done');
      },*/
uploadTemplate: function (o) {
    var rows = $();
    $.each(o.files, function (index, file) {
       console.log(file.error);

        var row = $('<tr class="template-upload fade">' +
          //  '<td class="preview"><span class="fade"></span></td>' +
            '<td class="name"></td>' +
            //'<td class="size"></td>' +
            (file.error ? '<td class="error" colspan="2"></td>' :
               '<td class="progress_wrapper">' +
               '<div class="progress">' +
               '<div class="bar" style="width:0%;"></div></div></td>'
            ) + '<td class="cancel"><button class="button_action delete_button">X</button></td></tr>');
        row.find('.name').text(file.name);
        row.find('.size').text(o.formatFileSize(file.size));
        if (file.error) {
            row.find('.error').text(
                locale.fileupload.errors[file.error] || file.error
            );
        }
        rows = rows.add(row);
    });
    return rows;
},
downloadTemplate: function (o) {
    var rows = $();
    $.each(o.files, function (index, file) {
        console.log(file);
        var row = $('<tr class="template-download fade">' +
            (file.error ? '<td></td><td class="name"></td>' +
                '<td class="size"></td><td class="error" colspan="2"></td>' :
        //            '<td class="preview"></td>' +
                        '<td class="name"><a></a></td>'
            //            '<td class="size"></td><td colspan="2"></td>'
            ));
        //row.find('.size').text(o.formatFileSize(file.size));
        if (file.error) {
            row.find('.name').text(file.name);
            row.find('.error').text(
                locale.fileupload.errors[file.error] || file.error
            );
        } else {
            row.find('.name a').text(file.name);
            /*if (file.thumbnail_url) {
                row.find('.preview').append('<a><img></a>')
                    .find('img').prop('src', file.thumbnail_url);
                row.find('a').prop('rel', 'gallery');
            }*/
        //    row.find('a').prop('href', file.url);
            /*row.find('.delete button')
                .attr('data-type', file.delete_type)
                .attr('data-url', file.delete_url);*/
        }
        rows = rows.add(row);
    });
    return rows;
}
});
});
