#from db.models import db, Student, Allocation  # assuming these are defined
#from sqlalchemy.orm import joinedload

#def get_allocations(student_id=None, classroom_id=None):
#    query = db.session.query(Allocation).options(joinedload(Allocation.student))

#    if student_id:
#        query = query.filter(Allocation.student_id == student_id)
#    if classroom_id is not None:
#        query = query.filter(Allocation.classroom_id == classroom_id)

#    results = query.all()

#    return [
#        {
#            "student_id": alloc.student_id,
#            "classroom_id": alloc.classroom_id,
#            "student_name": alloc.student.name if alloc.student else None
#        }
#        for alloc in results
#    ]
