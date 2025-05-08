from flask import Blueprint, request, jsonify
from db.db_manager import (
    assign_classroom_ml,
    update_allocation,
    get_allocations,
    get_students_in_classroom
)

allocations_bp = Blueprint("allocations", __name__)

# POST /allocate: Assign classrooms using ML
@allocations_bp.route("/allocate", methods=["POST"])
def allocate_students():
    data = request.get_json()
    student_ids = data.get("student_ids", [])

    if not student_ids:
        return jsonify({"error": "No student_ids provided"}), 400

    try:
        assignments = assign_classroom_ml(student_ids)
        return jsonify({"status": "success", "assignments": assignments})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /allocations: Get all allocations, or filter by student_id or classroom_id
@allocations_bp.route("/allocations", methods=["GET"])
def get_all_allocations():
    student_id = request.args.get("student_id")
    classroom_id = request.args.get("classroom_id", type=int)  # '0' means unallocated

    allocations = get_allocations(student_id=student_id, classroom_id=classroom_id)
    return jsonify(allocations)


# PUT /allocations/change: Move student to another classroom (or unallocate)
@allocations_bp.route("/allocations/change", methods=["PUT"])
def change_student_allocation():
    data = request.get_json()
    student_id = data.get("id")
    classroom_id = data.get("classroom_id")  # 1�4 or 0 for unallocated

    if not student_id or classroom_id is None:
        return jsonify({"error": "Missing id or classroom_id"}), 400

    success = update_allocation(student_id, classroom_id, source="manual")
    if not success:
        return jsonify({"error": "Update failed or student not found"}), 404

    return jsonify({
        "status": "updated",
        "student_id": student_id,
        "new_classroom": classroom_id
    })


# GET /classrooms/<classroom_id>/students: Get students in a specific classroom
@allocations_bp.route("/classrooms/<int:classroom_id>/students", methods=["GET"])
def students_in_classroom(classroom_id):
    students = get_students_in_classroom(classroom_id)
    return jsonify(students)


# GET /classrooms/unallocated/students: Get students with classroom_id = 0
@allocations_bp.route("/classrooms/unallocated/students", methods=["GET"])
def unallocated_students():
    students = get_students_in_classroom(0)
    return jsonify(students)


# GET /students: Get all students and their classroom assignments
@allocations_bp.route("/students", methods=["GET"])
def get_all_students():
    students = get_allocations()
    return jsonify(students)
