class Config:
    def __init__(self):
        self.my_email_address = 'XXX'
        self.password = 'XXX'
        self.dest = 'XXX'
        self.message_init = """


                                            <!-- Introduction -->
                                            <tr class="">
                                               <td class="grid__col" style="font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; padding: 32px 40px; border-radius:6px 6px 0 0;" align="">
                                                  <h2 style="color: #404040; font-weight: 300; margin: 0 0 12px 0; font-size: 24px; line-height: 30px; font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; " class="">
                                                     Hi Alexandre, </br>
                                                     {number_flash_cards} machine learning flashcards has been downloaded.
                                                  </h2>
                                                  <div style="color: #666666; font-weight: 400; font-size: 15px; line-height: 21px; font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; font-weight: 300; " class="organized_by">
                                                     Tweeted by <a href="https://twitter.com/chrisalbon" style="color:#999;" target="_blank">Chris Albon</a>
                                                  </div>
                                               </td>
                                            </tr>
                                            <tr>
                                               <td style="padding: 0 40px;">
                                                  <table cellspacing="0" cellpadding="0" width="100%" style="width: 100%; min-width: 100%;" class="">
                                                     <tr>
                                                        <td style="background-color: #dedede; width: 100%; min-width: 100%; font-size: 1px; height: 1px; line-height: 1px; " class="">&nbsp;
                                                        </td>
                                                     </tr>
                                                  </table>
                                               </td>
                                            </tr>
                                            <tr>
                                               <td class="table__ridge table__ridge--bottom">
                                                  <img src="https://cdn.evbstatic.com/s3-s3/marketing/emails/modules/ridges_bottom_fullx2.jpg" height="7" style="height:7px; border:none; display:block;" border="0" />
                                               </td>
                                            </tr>
                """

        self.intro = """\
        <!doctype html>
        <html xmlns="http://www.w3.org/1999/xhtml">
           <head>
              <meta name="viewport" content="width=device-width">
              <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
              <!-- Turn off iOS phone number autodetect -->
              <meta name="format-detection" content="telephone=no">
              <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
              <style>
                 body, p {
                 font-family: "Benton Sans", -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Helvetica, Tahoma, Arial, sans-serif;
                 -webkit-font-smoothing: antialiased;
                 -webkit-text-size-adjust: none;
                 }
                 table {
                 border-collapse: collapse;
                 border-spacing: 0;
                 border: 0;
                 padding: 0;
                 }
                 img {
                 margin: 0;
                 padding: 0;
                 }
                 .content {
                 width: 600px;
                 }
                 .no_text_resize {
                 -moz-text-size-adjust: none;
                 -webkit-text-size-adjust: none;
                 -ms-text-size-adjust: none;
                 text-size-adjust: none;
                 }
                 /* Media Queries */
                 @media all and (max-width: 600px) {
                 table[class="content"] {
                 width: 100% !important;
                 }
                 tr[class="grid-no-gutter"] td[class="grid__col"] {
                 padding-left: 0 !important;
                 padding-right: 0 !important;
                 }
                 td[class="grid__col"] {
                 padding-left: 15px !important;
                 padding-right: 15px !important;
                 }
                 tr[class="small_full_width"] td[class="grid__col"] {
                 padding-left: 0px !important;
                 padding-right: 0px !important;
                 }
                 table[class="small_full_width"] {
                 width: 100% !important;
                 padding-bottom: 10px;
                 }
                 a[class="header-link"] {
                 margin-right: 0 !important;
                 margin-left: 10px !important;
                 }
                 a[class="btn"] {
                 width: 100%;
                 border-left-width: 0px !important;
                 border-right-width: 0px !important;
                 }
                 table[class="col-layout"] {
                 width: 100% !important;
                 }
                 td[class="col-container"] {
                 display: block !important;
                 width: 100% !important;
                 padding-left: 0 !important;
                 padding-right: 0 !important;
                 }
                 td[class="col-nav-items"] {
                 display: inline-block !important;
                 padding-left: 0 !important;
                 padding-right: 10px !important;
                 background: none !important;
                 }
                 img[class="col-img"] {
                 height: auto !important;
                 max-width: 520px !important;
                 width: 100% !important;
                 }
                 td[class="col-center-sm"] {
                 text-align: center;
                 }
                 tr[class="footer-attendee-cta"] > td[class="grid__col"] {
                 padding: 24px 0 0 !important;
                 }
                 td[class="col-footer-cta"] {
                 padding-left: 0 !important;
                 padding-right: 0 !important;
                 }
                 td[class="footer-links"] {
                 text-align: left !important;
                 }
                 .hide-for-small {
                 display: none !important;
                 }
                 .ribbon-mobile {
                 line-height: 1.3 !important;
                 }
                 .small_full_width {
                 width: 100% !important;
                 padding-bottom: 10px;
                 }
                 .table__ridge {
                 height: 7px !important;
                 }
                 .table__ridge img {
                 display: none !important;
                 }
                 .table__ridge--top {
                 background-image: url(https://cdn.evbstatic.com/s3-s3/marketing/emails/modules/ridges_top_fullx2.jpg) !important;
                 background-size: 170% 7px;
                 }
                 .table__ridge--bottom {
                 background-image: url(https://cdn.evbstatic.com/s3-s3/marketing/emails/modules/ridges_bottom_fullx2.jpg) !important;
                 background-size: 170% 7px;
                 }
                 .summary-table__total {
                 padding-right: 10px !important;
                 }
                 .app-cta {
                 display: none !important;
                 }
                 .app-cta__mobile {
                 width: 100% !important;
                 height: auto !important;
                 max-height: none !important;
                 overflow: visible !important;
                 float: none !important;
                 display: block !important;
                 margin-top: 12px !important;
                 visibility: visible;
                 font-size: inherit !important;
                 }
                 .list-card__header {
                 width: 130px !important;
                 }
                 .list-card__label {
                 width: 130px !important;
                 }
                 .list-card__image-wrapper {
                 width: 130px !important;
                 height: 65px !important;
                 }
                 .list-card__image {
                 max-width: 130px !important;
                 max-height: 65px !important;
                 }
                 .list-card__body {
                 padding-left: 10px !important;
                 }
                 .list-card__title {
                 margin-bottom: 10px !important;
                 }
                 .list-card__date {
                 padding-top: 0 !important;
                 }
                 }
                 @media all and (device-width: 768px) and (device-height: 1024px) and (orientation:landscape) {
                 .ribbon-mobile {
                 line-height: 1.3 !important;
                 }
                 .ribbon-mobile__text {
                 padding: 0 !important;
                 }
                 }
                 @media all and (device-width: 768px) and (device-height: 1024px) and (orientation:portrait) {
                 .ribbon-mobile {
                 line-height: 1.3 !important;
                 }
                 .ribbon-mobile__text {
                 padding: 0 !important;
                 }
                 }
                 @media screen and (min-device-height:480px) and (max-device-height:568px), (min-device-width : 375px) and (max-device-width : 667px) and (-webkit-min-device-pixel-ratio : 2), (min-device-width : 414px) and (max-device-width : 736px) and (-webkit-min-device-pixel-ratio : 3) {
                 .hide_for_iphone {
                 display: none !important;
                 }
                 .passbook {
                 width: auto !important;
                 height: auto !important;
                 line-height: auto !important;
                 visibility: visible !important;
                 display: block !important;
                 max-height: none !important;
                 overflow: visible !important;
                 float: none !important;
                 text-indent: 0 !important;
                 font-size: inherit !important;
                 }
                 }
              </style>
           </head>
           <!-- Global container with background styles. Gmail converts BODY to DIV so we lose properties like BGCOLOR. -->
           <body border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" bgcolor="#F7F7F7" style="margin: 0;">
              <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" bgcolor="#F7F7F7">
                 <tr>
                    <td style="padding-right: 10px; padding-left: 10px;">
                                <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" bgcolor="white" style="width: 600px; max-width: 600px;">
                                   <tr>
                                      <td width="100%" valign="middle" style="text-align:center; padding:30px 0 20px 0;">
                                         <a href="https://www.twitter.com">
                                         <img src="https://raw.githubusercontent.com/alexattia/Data-Science-Projects/master/TwitterParsing/pic.png" width="715" height="70" border="0"  style="width:715px; height:70px;" />
                                         </a>
                                      </td>
                                   </tr>
                                </table>
                    </td>
                 </tr>
                 <tr>
                    <td>
                                <table class="content" align="center" cellpadding="0" cellspacing="0" border="0" bgcolor="#F7F7F7" style="width: 600px; max-width: 600px;">
                                   <tr>
                                      <td colspan="2" style="background: #fff; border-radius: 8px;">
                                         <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                               <td style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                                                  <style>
                                                     @media (max-device-width: 640px) {
                                                     .organized_by {
                                                     font-size: 14px !important;
                                                     }
                                                     .ticket-section__or {
                                                     padding: 12px 0 14px 0 !important;
                                                     }
                                                     .your-account__logo {
                                                     margin-top: 8px;
                                                     }
                                                     }
                                                     @media screen and (min-device-height:480px) and (max-device-height:568px) {
                                                     h2 {
                                                     font-weight: 600 !important;
                                                     }
                                                     .header_defer {
                                                     font-size: 12px;
                                                     }
                                                     }
                                                  </style>
"""
        self.flashcard = """
                                    <!-- Beginnning flash cards details  -->

                                    <tr class="">
                                       <td class="grid__col" style="font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; padding: 32px 40px; border-radius:0 0 6px 6px;" align="">
                                          <table cellpadding="0" cellspacing="0" border="0" align="left" style="width:260px; line-height:1.67; font-size:13px;" class="small_full_width ">
                                             <tr>
                                                <td>
                                                   <h2 style="color: #404040; font-weight: 300; margin: 0 0 12px 0; font-size: 24px; line-height: 30px; font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; " class="">
                                                      {tweet_text}
                                                   </h2>
                                                   <table cellspacing="0" cellpadding="0" width='100%' style='' align='' class="">
                                                      <tr style='' class=''>
                                                         <td width='20' height='' style='vertical-align:top; padding-right:10px;' align='' valign='' class='' colspan='1'>
                                                            <img src='https://cdn.evbstatic.com/s3-s3/marketing/emails/order_confirmation/date-iconx2.png' title='date' alt='date' style='width:20px; height:20px; vertical-align:-2px;' border="0" width='20' height='20' class=""/>
                                                         </td>
                                                         <td width='' height='' style='' align='' valign='' class='' colspan='1'>
                                                            <div style="color: #666666; font-weight: 400; font-size: 15px; line-height: 21px; font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; " class="">
                                                               {date}
                                                            </div>
                                                         </td>
                                                      </tr>
                                                   </table>
                                                </td>
                                             </tr>
                                          </table>
                                          <table cellpadding="0" cellspacing="0" border="0" align="right" style="width:240px; text-align: center; margin-top:16px;" class="small_full_width ">
                                             <tr>
                                                <td>
                                                   <img src={link_picture} title='map' alt='map' style='width:240px; height:160px' border="0" width='240' height='160' class="hide-for-small"/> 
                                                </td>
                                             </tr>
                                          </table>
                                       </td>
                                    </tr>

                                    <!-- Line Separator -->
                                    <tr>
                                       <td style="padding: 0 40px;">
                                          <table cellspacing="0" cellpadding="0" width="100%" style="width: 100%; min-width: 100%;" class="">
                                             <tr>
                                                <td style="background-color: #dedede; width: 100%; min-width: 100%; font-size: 1px; height: 1px; line-height: 1px; " class="">&nbsp;
                                                </td>
                                             </tr>
                                          </table>
                                       </td>
                                    </tr>
        """

        self.end = """
                                                    </td>
                                            </tr>
                                         </table>
                                      </td>
                                   </tr>
                                </table>
                    </td>
                 </tr>
              </table>
           </body>
        </html>
        """