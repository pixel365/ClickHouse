#pragma once

#include <string>
#include <vector>

/* Protobuf generated files give lots of warnings, disable them */
#if defined(__clang__)
#    pragma clang diagnostic push
#    pragma clang diagnostic ignored "-Wno-everything"
#endif

#include "SQLGrammar.pb.h"

#if defined(__clang__)
#    pragma clang diagnostic pop
#endif

namespace BuzzHouse
{

void SQLQueryToString(std::string & ret, const SQLQuery &);

}
