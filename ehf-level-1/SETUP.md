# Connect registration

The page works before this. Until the endpoint below is filled in, it prepares an email to quanyin144@gmail.com.

1. Open https://script.google.com while signed in as the Google account that should own the sheet and send the notice (quanyin144@gmail.com).
2. Create a project, replace the default file with the contents of `ehf-level-1/apps-script/Code.gs`, and save.
3. Choose `setup` in the function menu and run it. Approve the spreadsheet and email prompts. The log shows the new Google Sheet URL. Keep that sheet private.
4. Deploy, New deployment, type Web app. Execute as **Me**. Who has access: **Anyone**. Deploy and copy the URL that ends in `/exec`.
5. Paste that URL into `ehf-level-1/config.js` as `EHF_ENDPOINT`, then publish that one-line change.

The page then saves each registration, emails quanyin144@gmail.com, and shows spots remaining plus the potluck list (first names and dishes only).
