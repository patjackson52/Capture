package com.capture.app.data

import android.util.Log
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.concurrent.ConcurrentLinkedDeque

/**
 * In-app logger that keeps a ring buffer of recent log entries.
 * Also forwards to Logcat. Intended for diagnosing save failures
 * that are hard to reproduce.
 */
object AppLogger {

    enum class Level { DEBUG, INFO, ERROR }

    data class Entry(
        val timestamp: LocalDateTime,
        val level: Level,
        val tag: String,
        val message: String,
        val throwable: Throwable? = null
    ) {
        private companion object {
            val FMT: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSS")
        }

        fun format(): String = buildString {
            append(timestamp.format(FMT))
            append("  ")
            append(level.name.padEnd(5))
            append("  [")
            append(tag)
            append("]  ")
            append(message)
            throwable?.let {
                append("\n    ")
                append(it::class.simpleName)
                append(": ")
                append(it.message)
            }
        }
    }

    private const val MAX_ENTRIES = 500
    private const val LOGCAT_TAG = "Capture"

    private val entries = ConcurrentLinkedDeque<Entry>()

    fun d(tag: String, message: String) = log(Level.DEBUG, tag, message)
    fun i(tag: String, message: String) = log(Level.INFO, tag, message)
    fun e(tag: String, message: String, throwable: Throwable? = null) =
        log(Level.ERROR, tag, message, throwable)

    private fun log(level: Level, tag: String, message: String, throwable: Throwable? = null) {
        val entry = Entry(
            timestamp = LocalDateTime.now(),
            level = level,
            tag = tag,
            message = message,
            throwable = throwable
        )
        entries.addLast(entry)
        while (entries.size > MAX_ENTRIES) {
            entries.pollFirst()
        }

        // Forward to Logcat
        val logcatTag = "$LOGCAT_TAG/$tag"
        when (level) {
            Level.DEBUG -> Log.d(logcatTag, message, throwable)
            Level.INFO -> Log.i(logcatTag, message, throwable)
            Level.ERROR -> Log.e(logcatTag, message, throwable)
        }
    }

    fun allEntries(): List<Entry> = entries.toList()

    fun clear() = entries.clear()

    fun dump(): String = allEntries().joinToString("\n") { it.format() }
}
