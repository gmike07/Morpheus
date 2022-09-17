/* -*-mode:c++; tab-width: 2; indent-tabs-mode: nil; c-basic-offset: 2 -*- */
#include "cc_logging_objects.hh"
#include <string>

using json = nlohmann::json;

void ScoreHandler::operator()()
{
  if(not socket_helper.is_new_chunk_scoring)
  {
    return;
  }
  if(not socket_helper.is_valid_score_type())
  {
    socket_helper.is_new_chunk_scoring = false;
    return;
  }
  double score = socket_helper.get_qoe();
  std::string s = socket_helper.get_congestion_control() + " " + std::to_string(score);
  if(not pref.empty())
  {
    s = pref + " " + s;
  }
  std::cout << s << std::endl;
  scoring_file << score << std::endl;
  socket_helper.is_new_chunk_scoring = false;
}

std::string ServerSender::send_and_receive_str(const std::string& str)
{
  json data;
  data["message"] = str;
  return send_and_receive(data);
}

// std::pair<int, std::string> ServerSender::send_and_receive(json& js)
// {
//   js["server_id"] = server_id;
//   std::ostringstream response;
//   std::list<std::string> header;
//   header.push_back("Content-Type: application/json");

//   curlpp::Cleanup clean;
//   curlpp::Easy request;
//   request.setOpt(new curlpp::options::Url(host));
//   request.setOpt(new curlpp::options::HttpHeader(header));
//   request.setOpt(new curlpp::options::PostFields(js.dump()));
//   request.setOpt(new curlpp::options::PostFieldSize(js.dump().size()));
//   request.setOpt(new curlpp::options::WriteStream(&response));
//   try {
//     request.perform(); // 200 = ok and not enough data to switch, 409 = ok and sent json with {"cc": cc_to switch to}
//     long status = curlpp::infos::ResponseCode::get(request);
//     return {status, response.str()};
//   }
//   catch (std::exception& e) {
//     std::cout << "exception " << e.what() << std::endl;
//   }
//   return {-1, "error"};
// }

std::string ServerSender::send_and_receive(json& js)
{
  js["server_id"] = server_id;
  char buffer[1048576] = {0};
  strcpy(buffer, (js.dump() + "\n").c_str());
  
  write(sock_, buffer, 1048576);

  char recv_buf[100] = {0};
  read(sock_, recv_buf, 100);
  std::string response(recv_buf);
  return response.substr(0, response.find('\n'));
}



int ServerSender::send(std::vector<double>& state, bool stateless)
{ 
  json data;
  if(not stateless)
  {
    json json_state(state);
    data["state"] = json_state;
    std::vector<double> helper = {socket_helper.chosen_ssim, std::abs(socket_helper.chosen_ssim - socket_helper.get_ssim()), socket_helper.get_rebuffer()};
    json json_state_qoe(helper);
    data["qoe_state"] = json_state_qoe;
    data["curr_cc"] = socket_helper.get_congestion_control();
  }
  else
  {
    data["stateless"] = "stateless";
  }
  data["qoe"] = socket_helper.get_qoe();
  data["normalized qoe"] = socket_helper.get_normalized_qoe();

  std::string response = send_and_receive(data);
  try {
    auto js = json::parse(response);
    return std::stoi(js["cc"].get<std::string>());
  }
  catch (std::exception& e) {
    std::cout << "exception " << e.what() << std::endl;
    std::cout << "the response is: " << response << " for server " << socket_helper.server_id << std::endl;
    clear_buff();
  }
  return -1;
}

void ServerSender::send_state_and_replace_cc(std::vector<double> state, bool stateless)
{
  int cc_index = send(state, stateless);
  if(cc_index != -1)
  {
    change_cc(socket_helper, cc_index);
  }
}


void StateServerHandler::operator()()
{
  history_p.get()->update_chunk(start_time);
  counter = (counter + 1) % nn_roundup;
  bool change_cc_1 = (abr_time and socket_helper.is_new_chunk_model);
  socket_helper.is_new_chunk_model = false;
  bool change_cc_2 = ((not abr_time) and (counter % nn_roundup == 0));
  if((not change_cc_1) and (not change_cc_2))
  {
    return;
  }
  //should change cc
  history_p.get()->push_chunk();
  history_p.get()->push_statistic();
  start_time = get_timestamp_ms();
  if(history_p.get()->size() != ((size_t) socket_helper.history_size))
  {
    if(socket_helper.stateless)
    {
      std::thread([this](){sender.send_state_and_replace_cc({}, true);}).detach();
    }
    return;
  }
  std::vector<double> state(0);
  history_p.get()->get_state(state);
  std::thread([this, state](){sender.send_state_and_replace_cc(state);}).detach();
}


// void StatelessServerHandler::operator()()
// {
//   counter = (counter + 1) % nn_roundup;
//   bool change_cc_1 = (abr_time and socket.is_new_chunk_model);
//   socket.is_new_chunk_model = false;
//   bool change_cc_2 = ((not abr_time) and (counter % nn_roundup == 0));
//   if((not change_cc_1) and (not change_cc_2))
//   {
//     return;
//   }
//   //should change cc
//   std::vector<double> state(0);
//   std::thread([this, state](){sender.send_state_and_replace_cc(state);}).detach();
// }