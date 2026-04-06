from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

db = {
    "operations": [],
    "operationLogs": []
}

operation_id_counter = 1

@app.route("/api/roblox/join", methods=["POST"])
def join():
    global operation_id_counter
    try:
        data = request.get_json()
        invite_code = data.get("inviteCode")
        token_ids = data.get("tokenIds")
        user_id = data.get("userId")

        if not invite_code or not token_ids or not user_id:
            return jsonify({"error": "Missing required fields"}), 400

        operation_id = operation_id_counter
        operation_id_counter += 1

        db["operations"].append({
            "id": operation_id,
            "userId": user_id,
            "type": "join",
            "status": "pending",
            "targetId": invite_code,
            "tokenCount": len(token_ids),
            "createdAt": datetime.now().isoformat()
        })

        for token_id in token_ids:
            db["operationLogs"].append({
                "operationId": operation_id,
                "tokenId": token_id,
                "status": "pending",
                "message": "Queued for execution",
                "createdAt": datetime.now().isoformat()
            })

        return jsonify({
            "success": True,
            "operationId": operation_id,
            "message": "Join operation started"
        })
    except Exception as e:
        print(f"Join error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/roblox/leave", methods=["POST"])
def leave():
    global operation_id_counter
    try:
        data = request.get_json()
        guild_id = data.get("guildId")
        token_ids = data.get("tokenIds")
        user_id = data.get("userId")

        if not guild_id or not token_ids or not user_id:
            return jsonify({"error": "Missing required fields"}), 400

        operation_id = operation_id_counter
        operation_id_counter += 1

        db["operations"].append({
            "id": operation_id,
            "userId": user_id,
            "type": "leave",
            "status": "pending",
            "targetId": guild_id,
            "tokenCount": len(token_ids),
            "createdAt": datetime.now().isoformat()
        })

        for token_id in token_ids:
            db["operationLogs"].append({
                "operationId": operation_id,
                "tokenId": token_id,
                "status": "pending",
                "message": "Queued for execution",
                "createdAt": datetime.now().isoformat()
            })

        return jsonify({
            "success": True,
            "operationId": operation_id,
            "message": "Leave operation started"
        })
    except Exception as e:
        print(f"Leave error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/roblox/spam", methods=["POST"])
def spam():
    global operation_id_counter
    try:
        data = request.get_json()
        channel_id = data.get("channelId")
        message = data.get("message")
        token_ids = data.get("tokenIds")
        user_id = data.get("userId")

        if not channel_id or not message or not token_ids or not user_id:
            return jsonify({"error": "Missing required fields"}), 400

        operation_id = operation_id_counter
        operation_id_counter += 1

        db["operations"].append({
            "id": operation_id,
            "userId": user_id,
            "type": "spam",
            "status": "pending",
            "targetId": channel_id,
            "tokenCount": len(token_ids),
            "metadata": {"message": message},
            "createdAt": datetime.now().isoformat()
        })

        for token_id in token_ids:
            db["operationLogs"].append({
                "operationId": operation_id,
                "tokenId": token_id,
                "status": "pending",
                "message": "Queued for execution",
                "createdAt": datetime.now().isoformat()
            })

        return jsonify({
            "success": True,
            "operationId": operation_id,
            "message": "Spam operation started"
        })
    except Exception as e:
        print(f"Spam error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/roblox/operation/<int:operation_id>", methods=["GET"])
def get_operation(operation_id):
    try:
        operation = None
        for op in db["operations"]:
            if op["id"] == operation_id:
                operation = op
                break

        if not operation:
            return jsonify({"error": "Operation not found"}), 404

        logs = [log for log in db["operationLogs"] if log["operationId"] == operation_id]

        success_count = len([l for l in logs if l["status"] == "success"])
        failure_count = len([l for l in logs if l["status"] == "failed"])
        captcha_count = len([l for l in logs if "captcha" in l["message"].lower()])
        cloudflare_count = len([l for l in logs if "cloudflare" in l["message"].lower()])

        return jsonify({
            "id": operation["id"],
            "type": operation["type"],
            "status": operation["status"],
            "tokenCount": operation["tokenCount"],
            "successCount": success_count,
            "failureCount": failure_count,
            "captchaCount": captcha_count,
            "cloudflareCount": cloudflare_count,
            "createdAt": operation["createdAt"]
        })
    except Exception as e:
        print(f"Get operation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/roblox/operation/<int:operation_id>/logs", methods=["GET"])
def get_operation_logs(operation_id):
    try:
        logs = [log for log in db["operationLogs"] if log["operationId"] == operation_id]

        return jsonify({
            "logs": [
                {
                    "tokenId": log["tokenId"],
                    "status": log["status"],
                    "message": log["message"],
                    "createdAt": log["createdAt"]
                }
                for log in logs
            ]
        })
    except Exception as e:
        print(f"Get logs error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
