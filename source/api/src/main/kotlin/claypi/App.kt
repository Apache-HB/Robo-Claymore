/*
 * This Kotlin source file was generated by the Gradle 'init' task.
 */
package claypi

import com.mongodb.*
import com.mongodb.client.*
import com.mongodb.client.model.Filters.eq
import org.reactivestreams.Subscriber
import org.reactivestreams.Subscription
import org.bson.Document
import org.ini4j.*
import java.io.File

import com.serebit.strife.*

import kotlinx.coroutines.*

import io.ktor.application.*
import io.ktor.http.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*

fun config(path: String) = Wini(File(path))

fun Wini.getInt(head: String, field: String): Int? = this.get(head, field, Int::class.java)

const val API_VERSION = "/api/v1"
const val PREFIX_ENDPOINT = "$API_VERSION/prefix"

fun String.toJsonString(): String = "\"$this\""

fun Role.toJson() = """{ "id": ${this.id}, "name": "${this.name}", "colour": ${this.color.rgb} }"""

suspend fun main(args: Array<String>) {
    val cfg = config("../config/config.ini")

    val mongoUrl: String? = cfg.get("mongo", "url")
    val client = if(mongoUrl != null) MongoClients.create(mongoUrl) else MongoClients.create()
    val db = client.getDatabase(cfg.get("mongo", "name"))
    val prefixes = db.getCollection("prefix")
    val defaultPrefix = cfg.get("discord", "prefix")

    val port = cfg.getInt("api", "port")!!

    var discord: BotClient? = null

    GlobalScope.launch {
        bot(cfg.get("discord", "token")) {
            onReady {
                discord = context
                println("bot has logged in")
            }
        }
    }

    embeddedServer(Netty, port) {
        routing {
            get("/") {
                call.respondText("Name jeff", ContentType.Text.Html)
            }
            get(PREFIX_ENDPOINT) {
                when(val id = call.parameters["id"]?.toLongOrNull()) {
                    null -> call.respondText("""{ "prefix": null }""")
                    else -> {
                        val prefix = prefixes.find(eq("id", id)).first()?.get("prefix") as String?
                        call.respondText("""{ "prefix": ${prefix?.toJsonString()} }""", ContentType.Application.Json)
                    }
                }
            }
            get("$PREFIX_ENDPOINT/global") {
                call.respondText("""{ "prefix": "$defaultPrefix" }""", ContentType.Application.Json)
            }
            get("/role") {
                when(val id = call.parameters["id"]?.toLongOrNull()) {
                    null -> call.respondText("""{ "valid": false }""")
                    else -> discord?.getRole(id)?.let {
                        call.respondText(it.toJson(),ContentType.Application.Json)
                    }
                }
            }
        }
    }.start(wait = true)
}