package io.github.manojhunasimarad.kitchen;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Calendar;

/** Daily pantry-check notifications at the times chosen in the app's Settings. */
public class Reminders extends BroadcastReceiver {
    static final String PREFS = "reminders", CHANNEL = "pantry-check";
    static final int MAX = 4;

    /** Saves the settings sent by the page ({"on":true,"times":["08:00","19:30"],"text":"..."}) and reschedules. */
    static void save(Context c, String json) {
        try {
            JSONObject o = new JSONObject(json);
            c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putBoolean("on", o.optBoolean("on", false))
                .putString("times", o.optJSONArray("times") == null ? "[]" : o.getJSONArray("times").toString())
                .putString("text", o.optString("text", ""))
                .apply();
        } catch (Exception ignored) { }
        schedule(c);
    }

    static void schedule(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        SharedPreferences p = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        JSONArray times;
        try { times = new JSONArray(p.getString("times", "[]")); } catch (Exception e) { times = new JSONArray(); }
        for (int i = 0; i < MAX; i++) {
            PendingIntent pi = pending(c, i);
            am.cancel(pi);
            if (!p.getBoolean("on", false) || i >= times.length()) continue;
            String[] hm = times.optString(i, "").split(":");
            if (hm.length != 2) continue;
            Calendar at = Calendar.getInstance();
            try {
                at.set(Calendar.HOUR_OF_DAY, Integer.parseInt(hm[0]));
                at.set(Calendar.MINUTE, Integer.parseInt(hm[1]));
            } catch (NumberFormatException e) { continue; }
            at.set(Calendar.SECOND, 0);
            at.set(Calendar.MILLISECOND, 0);
            if (at.getTimeInMillis() <= System.currentTimeMillis() + 30000) at.add(Calendar.DAY_OF_MONTH, 1);
            // Inexact but allowed while the phone is idle; needs no special alarm permission.
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at.getTimeInMillis(), pi);
        }
    }

    static PendingIntent pending(Context c, int i) {
        Intent it = new Intent(c, Reminders.class).putExtra("slot", i);
        return PendingIntent.getBroadcast(c, 100 + i, it, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    @Override
    public void onReceive(Context c, Intent intent) {
        String action = intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action) || Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)
                || Intent.ACTION_TIME_CHANGED.equals(action) || Intent.ACTION_TIMEZONE_CHANGED.equals(action)) {
            schedule(c);
            return;
        }
        notify(c);
        schedule(c); // set tomorrow's
    }

    static void notify(Context c) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Pantry check", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Twice-daily reminder to tick what you have");
            nm.createNotificationChannel(ch);
        }
        Intent open = new Intent(c, MainActivity.class).putExtra("open", "check").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(c, 1, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        String text = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString("text", "");
        if (text == null || text.isEmpty()) text = "Two-minute check of what you have.";
        android.app.Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new android.app.Notification.Builder(c, CHANNEL) : new android.app.Notification.Builder(c);
        b.setSmallIcon(R.drawable.ic_stat_check)
            .setContentTitle("Pantry check")
            .setContentText(text)
            .setStyle(new android.app.Notification.BigTextStyle().bigText(text))
            .setContentIntent(pi)
            .setAutoCancel(true);
        try { nm.notify(7, b.build()); } catch (SecurityException ignored) { }
    }
}
